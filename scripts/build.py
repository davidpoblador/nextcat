# ABOUTME: CLI entrypoint for the NextCat document pipeline.
# ABOUTME: Orchestrates PDF builds for all languages using typer and rich.

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional

import typer
import typst
from rich.console import Console

from scripts.generate import (
    BUILD_DIR,
    CANONICAL_DIR,
    CONFIG_FILE,
    ROOT,
    TRANSLATIONS_DIR,
    build_typst,
    get_version,
    load_toml,
    resolve_chapters,
)

FONTS_DIR = ROOT / "fonts"

VARIANTS: list[tuple[str, bool]] = [
    ("", False),
    ("-full", True),
]

app = typer.Typer(help="Xarter document pipeline.")
console = Console()


def _compile_typst(typ_file: Path, version: str, lang: str, suffix: str) -> Path:
    """Compile a .typ file to PDF and remove the intermediate file."""
    pdf_file = BUILD_DIR / f"nextcat-{version}.{lang}{suffix}.pdf"
    label = f"{lang}{suffix}"
    try:
        compiler = typst.Compiler(
            input=typ_file,
            root=ROOT,
            font_paths=[FONTS_DIR],
        )
        compiler.compile(output=pdf_file)
        console.print(f"  [green]✓[/green] [{label}] {pdf_file.relative_to(ROOT)}")
    except typst.TypstError as exc:
        console.print(f"  [red]✗[/red] [{label}] {exc.message}")
    finally:
        typ_file.unlink()
    return pdf_file


@app.command()
def build(
    lang: Optional[str] = typer.Argument(None, help="Build only this language (e.g. 'ca', 'en')."),
) -> None:
    """Build PDFs for all available languages, or a single one."""
    config = load_toml(CONFIG_FILE)
    version = get_version()

    canonical_strings = load_toml(CANONICAL_DIR / "strings.toml")
    canonical_fm, canonical_ch = resolve_chapters(CANONICAL_DIR, CANONICAL_DIR)
    canonical_lang = canonical_strings["lang"]

    console.print(f"[bold cyan][{canonical_lang}][/bold cyan] Canonical · {len(canonical_ch)} chapters")

    # Collect (typ_file, lang, suffix) across languages and variants
    builds: list[tuple[Path, str, str]] = []

    def queue(content_dir: Path, strings: dict, fm, ch, notice: str = "") -> None:
        trans_lang = strings["lang"]
        for suffix, include_changelog in VARIANTS:
            typ_file = build_typst(
                content_dir,
                strings,
                config,
                version,
                fm,
                ch,
                notice,
                include_changelog=include_changelog,
                variant_suffix=suffix,
            )
            builds.append((typ_file, trans_lang, suffix))

    if lang is None or lang == canonical_lang:
        queue(CANONICAL_DIR, canonical_strings, canonical_fm, canonical_ch)

    if TRANSLATIONS_DIR.exists():
        for lang_dir in sorted(TRANSLATIONS_DIR.iterdir()):
            strings_file = lang_dir / "strings.toml"
            if not lang_dir.is_dir() or not strings_file.exists():
                continue

            lang_strings = load_toml(strings_file)
            trans_lang = lang_strings["lang"]

            if lang is not None and trans_lang != lang:
                continue

            translation_notice = lang_strings.get("translation", {}).get("notice", "")
            fm, ch = resolve_chapters(lang_dir, CANONICAL_DIR)

            console.print(f"[bold cyan][{trans_lang}][/bold cyan] Translation · {len(ch)} chapters")
            queue(lang_dir, lang_strings, fm, ch, translation_notice)

    if not builds:
        console.print(f"[yellow]No matching language found: {lang}[/yellow]")
        raise typer.Exit(1)

    console.print(f"\nCompiling [bold]{len(builds)}[/bold] PDF(s)...")
    with ThreadPoolExecutor() as pool:
        pool.map(lambda args: _compile_typst(args[0], version, args[1], args[2]), builds)

    console.print("\n[green bold]Done.[/green bold]")


if __name__ == "__main__":
    app()
