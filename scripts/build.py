# ABOUTME: CLI entrypoint for the Xarter document pipeline.
# ABOUTME: Orchestrates PDF builds for all languages using typer and rich.

import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from scripts.generate import (
    BUILD_DIR,
    CANONICAL_DIR,
    CHANGELOG_FILE,
    CONFIG_FILE,
    ROOT,
    TRANSLATIONS_DIR,
    build_index,
    build_typst,
    get_version,
    load_toml,
    resolve_chapters,
)

app = typer.Typer(help="Xarter document pipeline.")
console = Console()


def _compile_typst(typ_file: Path, version: str, lang: str) -> Path:
    """Compile a .typ file to PDF and remove the intermediate file."""
    pdf_file = BUILD_DIR / f"xarter-{version}.{lang}.pdf"
    result = subprocess.run(
        ["typst", "compile", "--root", str(ROOT), str(typ_file), str(pdf_file)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        console.print(f"  [red]✗[/red] [{lang}] {result.stderr.strip()}")
    else:
        console.print(f"  [green]✓[/green] [{lang}] {pdf_file.relative_to(ROOT)}")
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

    # Website assets (always from canonical)
    index_path, mkdocs_path = build_index(
        canonical_strings["document"],
        canonical_strings,
        canonical_strings.get("site", {}),
        config["document"]["repo"],
        canonical_fm,
        canonical_ch,
    )
    console.print(f"  [dim]→[/dim] {index_path.relative_to(ROOT)}")
    console.print(f"  [dim]→[/dim] {mkdocs_path.relative_to(ROOT)}")

    # Collect languages
    builds: list[tuple[Path, str]] = []

    if lang is None or lang == canonical_lang:
        typ_file = build_typst(CANONICAL_DIR, canonical_strings, config, version, canonical_fm, canonical_ch)
        builds.append((typ_file, canonical_lang))

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

            typ_file = build_typst(lang_dir, lang_strings, config, version, fm, ch, translation_notice)
            builds.append((typ_file, trans_lang))

    if not builds:
        console.print(f"[yellow]No matching language found: {lang}[/yellow]")
        raise typer.Exit(1)

    console.print(f"\nCompiling [bold]{len(builds)}[/bold] PDF(s)...")
    with ThreadPoolExecutor() as pool:
        pool.map(lambda args: _compile_typst(args[0], version, args[1]), builds)

    console.print("\n[green bold]Done.[/green bold]")


if __name__ == "__main__":
    app()
