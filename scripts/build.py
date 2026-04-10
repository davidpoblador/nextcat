# ABOUTME: Generates Typst documents and website assets for all languages.
# ABOUTME: Reads config, strings, and chapters from xarter/ and translations/*/.

import re
import shutil
import subprocess
import tomllib
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from babel.dates import format_date
from dunamai import Style, Version

ROOT = Path(__file__).resolve().parent.parent
CANONICAL_DIR = ROOT / "xarter"
TRANSLATIONS_DIR = ROOT / "translations"
CONFIG_FILE = CANONICAL_DIR / "config.toml"
VERSION_FILE = ROOT / "VERSION"
AUTHORS_FILE = ROOT / "AUTHORS"
CHANGELOG_FILE = ROOT / "CHANGELOG.md"
BUILD_DIR = ROOT / "build"
EXCLUDED_MD = {"index.md", "license.md", "about-author.md", "changelog.md"}


def load_toml(path: Path) -> dict:
    """Load a TOML file."""
    with open(path, "rb") as f:
        return tomllib.load(f)


def escape_typst(s: str) -> str:
    """Escape a string for safe inclusion in a Typst string literal."""
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("#", "\\#")


def escape_typst_content(s: str) -> str:
    """Escape a string for safe inclusion in Typst content mode."""
    return s.replace("\\", "\\\\").replace("#", "\\#").replace("_", "\\_").replace("*", "\\*")


def last_modified_date(files: list[Path]) -> str:
    """Most recent filesystem mtime across the given files."""
    mtimes = [f.stat().st_mtime for f in files if f.exists()]
    if not mtimes:
        return "-"
    dt = datetime.fromtimestamp(max(mtimes), tz=timezone.utc)
    return dt.strftime("%d/%m/%Y %H:%M UTC")


def generation_date() -> str:
    """Current timestamp formatted for display."""
    return datetime.now(tz=timezone.utc).strftime("%d/%m/%Y %H:%M UTC")


def cover_date(lang: str) -> str:
    """Current date formatted as 'Month Year' in the given language."""
    result = format_date(datetime.now(tz=timezone.utc), "LLLL yyyy", locale=lang)
    return result[0].upper() + result[1:]


def get_version() -> str:
    """Get the current version string from git tags or VERSION file."""
    try:
        return Version.from_git().serialize(style=Style.Pep440)
    except RuntimeError:
        return VERSION_FILE.read_text().strip()


def parse_changelog(path: Path) -> list[tuple[str, list[str]]]:
    """Parse a release-please CHANGELOG.md into [(version, [items])]."""
    versions: list[tuple[str, list[str]]] = []
    current_version: str | None = None
    current_items: list[str] = []

    for line in path.read_text().splitlines():
        version_match = re.match(r"^##\s+\[?(\d+\.\d+\.\d+)", line)
        if version_match:
            if current_version:
                versions.append((current_version, current_items))
            current_version = version_match.group(1)
            current_items = []
            continue
        if line.startswith("###"):
            continue
        if line.startswith("* "):
            text = line[2:]
            text = re.sub(r"\s*\(\[?[a-f0-9]{7,}\]?\(?[^)]*\)?\)\s*$", "", text)
            text = re.sub(r"\s*\(\[#\d+\]\([^)]+\)\)\s*$", "", text)
            text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
            text = text.strip()
            if text:
                current_items.append(text)

    if current_version:
        versions.append((current_version, current_items))

    return versions


def changelog_to_typst(versions: list[tuple[str, list[str]]], version_label: str) -> list[str]:
    """Convert parsed changelog to Typst headings and lists."""
    lines: list[str] = []
    for ver, items in versions:
        lines.append(f'   heading(level: 3)[{version_label} {ver}]')
        for item in items:
            lines.append(f"   [- {escape_typst_content(item)}]")
        lines.append("")
    return lines


def chapter_title(path: Path) -> str:
    """Extract the first top-level heading from a markdown file."""
    for line in path.read_text().splitlines():
        match = re.match(r"^#\s+(.+)$", line)
        if match:
            return match.group(1)
        match2 = re.match(r"^##\s+(.+)$", line)
        if match2:
            return match2.group(1)
    return path.stem


def resolve_chapters(content_dir: Path, canonical_dir: Path) -> tuple[list[Path], list[Path]]:
    """Resolve front matter and chapters, falling back to canonical for missing files."""
    canonical_md = sorted(canonical_dir.glob("*.md"))
    canonical_fm = [f for f in canonical_md if f.name.startswith("00-")]
    canonical_ch = [f for f in canonical_md if not f.name.startswith("00-") and f.name not in EXCLUDED_MD]

    if content_dir == canonical_dir:
        return canonical_fm, canonical_ch

    # For translations: use translated file if it exists, otherwise canonical
    front_matter = []
    for f in canonical_fm:
        translated = content_dir / f.name
        front_matter.append(translated if translated.exists() else f)

    chapters = []
    for f in canonical_ch:
        translated = content_dir / f.name
        chapters.append(translated if translated.exists() else f)

    return front_matter, chapters


def typst_param(key: str, value: str) -> str:
    """Format a Typst named parameter with an escaped string value."""
    return f'  {key}: "{escape_typst(value)}",'


def build_index(
    doc_strings: dict,
    strings: dict,
    site: dict,
    repo: str,
    front_matter: list[Path],
    chapter_files: list[Path],
) -> None:
    """Generate the mkdocs index.md from chapter files and strings."""
    lines = [
        f"# {doc_strings['title']}",
        "",
        f"*{doc_strings['subtitle']}*",
        "",
    ]

    for fm in front_matter:
        lines.append(f"- [{chapter_title(fm)}]({fm.name})")
    for ch in chapter_files:
        lines.append(f"1. [{chapter_title(ch)}]({ch.name})")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(site["downloads_text"].format(repo=repo))
    lines.append("")
    lines.append(site["license_text"])
    lines.append("")

    index_file = CANONICAL_DIR / "index.md"
    index_file.write_text("\n".join(lines))
    print(f"  Written {index_file.relative_to(ROOT)}")

    # Generate mkdocs.yml with nav from template
    mkdocs_template = ROOT / "templates" / "mkdocs.yml"
    mkdocs_output = ROOT / "mkdocs.yml"
    nav_lines = [
        "",
        "nav:",
        "  - Inici: index.md",
    ]
    for fm in front_matter:
        nav_lines.append(f"  - {chapter_title(fm)}: {fm.name}")
    for ch in chapter_files:
        nav_lines.append(f"  - {chapter_title(ch)}: {ch.name}")
    # Annex
    appendix = strings.get("appendix", {})
    nav_lines.append(f"  - {appendix.get('title', 'Annex')}:")
    nav_lines.append(f"    - {appendix.get('license_title', 'Llicència')}: license.md")
    about_author_file = CANONICAL_DIR / "about-author.md"
    if about_author_file.exists():
        about_nav_title = appendix.get("about_author_title", "Sobre l'autor")
        nav_lines.append(f"    - {about_nav_title}: about-author.md")
    if CHANGELOG_FILE.exists():
        # Copy changelog into docs dir for mkdocs
        shutil.copy(CHANGELOG_FILE, CANONICAL_DIR / "changelog.md")
        changelog = strings.get("changelog", {})
        nav_lines.append(f"    - {changelog.get('title', 'Registre de canvis')}: changelog.md")

    mkdocs_output.write_text(mkdocs_template.read_text() + "\n".join(nav_lines) + "\n")
    print(f"  Written {mkdocs_output.relative_to(ROOT)}")


def build_typst(
    content_dir: Path,
    strings: dict,
    config: dict,
    version: str,
    front_matter: list[Path],
    chapter_files: list[Path],
    translation_notice: str = "",
) -> None:
    """Generate a Typst document for one language."""
    doc = config["document"]
    doc_strings = strings["document"]
    title_page = strings["title_page"]
    toc = strings["toc"]
    changelog = strings["changelog"]
    colophon = strings["colophon"]
    lang = strings["lang"]

    content_files = [*front_matter, *chapter_files, CONFIG_FILE]
    generated_text = f'{title_page["generated"]}: {generation_date()}'
    modified_text = f'{title_page["modified"]}: {last_modified_date(content_files)}'

    parts: list[str] = [
        '#import "@preview/cmarker:0.1.8": render',
        '#import "../templates/template.typ": project',
        "",
        "#show: project.with(",
        typst_param("title", doc_strings["title"]),
        typst_param("subtitle", doc_strings["subtitle"]),
        typst_param("author", doc["author"]),
        typst_param("email", doc["email"]),
        typst_param("lang", lang),
        typst_param("toc-title", toc["title"]),
        typst_param("version", version),
        typst_param("version-label", title_page.get("version_label", "Versió")),
        typst_param("cover-date", cover_date(lang)),
        typst_param("url", doc["url"]),
        typst_param("repo", doc["repo"]),
        typst_param("generated-text", generated_text),
        typst_param("modified-text", modified_text),
        typst_param("modified-label", title_page["modified"]),
        typst_param("generated-label", title_page["generated"]),
        typst_param("translation-notice", translation_notice),
        ")",
        "",
    ]

    if front_matter:
        parts.append("// Front matter (unnumbered)")
        parts.append("#{ set heading(numbering: none, outlined: false)")
        for fm_file in front_matter:
            rel_path = fm_file.relative_to(ROOT)
            parts.append(f'   render(read("../{rel_path}"), h1-level: 2)')
        parts.append("}")
        parts.append("")

    # Table of contents
    toc_title = escape_typst(toc["title"])
    parts.append(f'#outline(title: "{toc_title}", depth: 2, indent: 1.5em)')
    parts.append("")

    # Display page numbers
    parts.append('#set page(numbering: "1", number-align: center)')
    parts.append("")

    for chapter_file in chapter_files:
        rel_path = chapter_file.relative_to(ROOT)
        parts.append(f"// Source: {rel_path}")
        parts.append(f'#render(read("../{rel_path}"), h1-level: 1)')
        parts.append("")

    # Appendix
    appendix = strings.get("appendix", {})
    appendix_title = escape_typst(appendix.get("title", "Annex"))
    parts.append(f'#{{ set heading(numbering: "A.1.")')
    parts.append(f'   counter(heading).update(0)')
    license_title = escape_typst(appendix.get("license_title", "Llicència"))
    parts.append(f'   heading(level: 1)[{appendix_title}]')
    parts.append(f'   heading(level: 2)[{license_title}]')
    license_file = content_dir / "license.md"
    license_path = f"../{license_file.relative_to(ROOT)}" if license_file.exists() else "../LICENSE"
    parts.append(f'   render(read("{license_path}"), h1-level: 3)')

    # About the author
    about_author_file = content_dir / "about-author.md"
    if not about_author_file.exists():
        about_author_file = CANONICAL_DIR / "about-author.md"
    if about_author_file.exists():
        about_title = escape_typst(appendix.get("about_author_title", "Sobre l'autor"))
        rel_path = f"../{about_author_file.relative_to(ROOT)}"
        parts.append(f'   heading(level: 2)[{about_title}]')
        parts.append(f'   render(read("{rel_path}"), h1-level: 3)')
        parts.append("")

    # Contributors
    if AUTHORS_FILE.exists():
        contributors_title = escape_typst(appendix.get("contributors_title", "Contribuïdors"))
        parts.append(f'   heading(level: 2)[{contributors_title}]')
        for line in AUTHORS_FILE.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            author_match = re.match(r"^(.+?)\s+<(.+?)>\s*$", line)
            if author_match:
                name = escape_typst(author_match.group(1))
                url = escape_typst(author_match.group(2))
                parts.append(f'   [- #link("{url}")[{name}]]')
            else:
                parts.append(f"   [- {escape_typst(line)}]")
        parts.append("")

    # Changelog
    if CHANGELOG_FILE.exists():
        changelog_title = escape_typst(changelog["title"])
        changelog_intro = escape_typst(changelog.get("intro", ""))
        cl_version_label = escape_typst(changelog.get("version_label", "Versió"))
        versions = parse_changelog(CHANGELOG_FILE)
        parts.append(f'   heading(level: 2)[{changelog_title}]')
        if changelog_intro:
            parts.append(f"   [{changelog_intro}]")
            parts.append("")
        parts.extend(changelog_to_typst(versions, cl_version_label))
    parts.append("}")
    parts.append("")

    # Colophon
    colophon_title = escape_typst(colophon["title"])
    colophon_text = escape_typst(colophon["text"])
    version_label = escape_typst(title_page.get("version_label", "Versió"))
    parts.append("#pagebreak()")
    parts.append("#v(1fr)")
    parts.append("#align(center)[")
    parts.append("#{ set heading(numbering: none)")
    parts.append("   show heading.where(level: 1): it => {")
    parts.append("     text(size: 20pt, weight: \"bold\")[#it.body]")
    parts.append("     v(1em)")
    parts.append("   }")
    parts.append(f'   heading(level: 1)[{colophon_title}]')
    parts.append("}")
    parts.append(f'  #text(fill: rgb("#555"))[{colophon_text}]')
    parts.append("")
    parts.append(f"  #v(1.5em)")
    parts.append(f'  {version_label}: {escape_typst(version)}')
    parts.append("")
    parts.append(f"  #v(1.5em)")
    parts.append(f'  {escape_typst(modified_text)} \\')
    parts.append(f'  {escape_typst(generated_text)}')
    parts.append("")
    parts.append(f"  #v(1.5em)")
    parts.append(f'  #set text(hyphenate: false)')
    parts.append(f'  #link("{escape_typst(doc["url"])}")[{escape_typst(doc["url"])}] \\')
    email_escaped = escape_typst(doc["email"]).replace("@", "\\@")
    parts.append(f'  #link("mailto:{escape_typst(doc["email"])}")[{email_escaped}]')
    parts.append("")
    parts.append(f"  #v(0.5em)")
    parts.append(f'  #link("{escape_typst(doc["repo"])}")[{escape_typst(doc["repo"])}]')
    parts.append("")
    if translation_notice:
        parts.append(f"  #v(1.5em)")
        parts.append(f'  #text(fill: rgb("#555"))[{escape_typst(translation_notice)}]')
    parts.append(f"  #v(1.5em)")
    parts.append('  #text(size: 8pt, fill: rgb("#999"))[CC BY-SA 4.0]')
    parts.append("]")
    parts.append("#v(1fr)")
    parts.append("")

    BUILD_DIR.mkdir(exist_ok=True)
    output_file = BUILD_DIR / f"document.{lang}.typ"
    output_file.write_text("\n".join(parts))
    return output_file


def compile_typst(typ_file: Path, version: str, lang: str) -> Path:
    """Compile a .typ file to PDF and remove the intermediate file."""
    pdf_file = BUILD_DIR / f"xarter-{version}.{lang}.pdf"
    result = subprocess.run(
        ["typst", "compile", "--root", str(ROOT), str(typ_file), str(pdf_file)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"  [{lang}] Error compiling: {result.stderr.strip()}")
    else:
        print(f"  [{lang}] {pdf_file.relative_to(ROOT)}")
    typ_file.unlink()
    return pdf_file


def build(lang_filter: str | None = None) -> None:
    """Build PDFs for all available languages, or a single one if lang_filter is set."""
    config = load_toml(CONFIG_FILE)
    version = get_version()

    # Canonical (Catalan)
    canonical_strings = load_toml(CANONICAL_DIR / "strings.toml")
    canonical_fm, canonical_ch = resolve_chapters(CANONICAL_DIR, CANONICAL_DIR)
    canonical_lang = canonical_strings["lang"]

    print(f"[{canonical_lang}] Building canonical version")
    for f in canonical_fm:
        print(f"  front matter: {f.name}")
    print(f"  {len(canonical_ch)} chapters")

    # Website assets (only for canonical)
    build_index(
        canonical_strings["document"],
        canonical_strings,
        canonical_strings.get("site", {}),
        config["document"]["repo"],
        canonical_fm,
        canonical_ch,
    )

    # Collect all languages to build
    builds: list[tuple[Path, str]] = []  # (typ_file, lang)

    if lang_filter is None or lang_filter == canonical_lang:
        typ_file = build_typst(CANONICAL_DIR, canonical_strings, config, version, canonical_fm, canonical_ch)
        builds.append((typ_file, canonical_lang))

    if TRANSLATIONS_DIR.exists():
        for lang_dir in sorted(TRANSLATIONS_DIR.iterdir()):
            strings_file = lang_dir / "strings.toml"
            if not lang_dir.is_dir() or not strings_file.exists():
                continue

            lang_strings = load_toml(strings_file)
            lang = lang_strings["lang"]

            if lang_filter is not None and lang != lang_filter:
                continue

            translation_notice = lang_strings.get("translation", {}).get("notice", "")
            fm, ch = resolve_chapters(lang_dir, CANONICAL_DIR)

            print(f"[{lang}] Building translation ({len(ch)} chapters)")

            typ_file = build_typst(lang_dir, lang_strings, config, version, fm, ch, translation_notice)
            builds.append((typ_file, lang))

    # Compile all languages in parallel
    print(f"Compiling {len(builds)} PDF(s)...")
    with ThreadPoolExecutor() as pool:
        pool.map(lambda args: compile_typst(args[0], version, args[1]), builds)


if __name__ == "__main__":
    import sys
    lang_filter = sys.argv[1] if len(sys.argv) > 1 else None
    build(lang_filter=lang_filter)
