# ABOUTME: Generates a Typst document that renders markdown chapters via cmarker.
# ABOUTME: Reads config, strings, and chapters from xarter/, writes document.typ.

import re
import tomllib
from datetime import datetime, timezone
from pathlib import Path

from babel.dates import format_date
from dunamai import Style, Version

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "xarter"
CONFIG_FILE = CONTENT_DIR / "config.toml"
STRINGS_FILE = CONTENT_DIR / "strings.toml"
VERSION_FILE = ROOT / "VERSION"
AUTHORS_FILE = ROOT / "AUTHORS"
CHANGELOG_FILE = ROOT / "CHANGELOG.md"
BUILD_DIR = ROOT / "build"
OUTPUT_FILE = BUILD_DIR / "document.typ"
INDEX_FILE = CONTENT_DIR / "index.md"


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
    # LLLL = standalone month name (not inflected)
    result = format_date(datetime.now(tz=timezone.utc), "LLLL yyyy", locale=lang)
    return result[0].upper() + result[1:]


def parse_changelog(path: Path) -> list[tuple[str, list[str]]]:
    """Parse a release-please CHANGELOG.md into [(version, [items])]."""
    versions: list[tuple[str, list[str]]] = []
    current_version: str | None = None
    current_items: list[str] = []

    for line in path.read_text().splitlines():
        # Version heading: ## [0.1.1](url) (2026-04-10)
        version_match = re.match(r"^##\s+\[?(\d+\.\d+\.\d+)", line)
        if version_match:
            if current_version:
                versions.append((current_version, current_items))
            current_version = version_match.group(1)
            current_items = []
            continue
        # Skip subsection headings (### Contingut nou, etc.)
        if line.startswith("###"):
            continue
        # List items: * text
        if line.startswith("* "):
            text = line[2:]
            # Strip commit hash references: ([hash](url)) or (hash)
            text = re.sub(r"\s*\(\[?[a-f0-9]{7,}\]?\(?[^)]*\)?\)\s*$", "", text)
            # Strip PR/issue references: ([#N](url))
            text = re.sub(r"\s*\(\[#\d+\]\([^)]+\)\)\s*$", "", text)
            # Strip bold scope prefixes: **deps:** -> deps:
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

    INDEX_FILE.write_text("\n".join(lines))
    print(f"Written {INDEX_FILE}")

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
    about_author_file = CONTENT_DIR / "about-author.md"
    if about_author_file.exists():
        about_nav_title = appendix.get("about_author_title", "Sobre l'autor")
        nav_lines.append(f"    - {about_nav_title}: about-author.md")

    mkdocs_output.write_text(mkdocs_template.read_text() + "\n".join(nav_lines) + "\n")
    print(f"Written {mkdocs_output}")


def typst_param(key: str, value: str) -> str:
    """Format a Typst named parameter with an escaped string value."""
    return f'  {key}: "{escape_typst(value)}",'


def build() -> None:
    """Read all chapter markdown files and produce a Typst document."""
    config = load_toml(CONFIG_FILE)
    strings = load_toml(STRINGS_FILE)

    doc = config["document"]
    doc_strings = strings["document"]
    title_page = strings["title_page"]
    toc = strings["toc"]
    changelog = strings["changelog"]
    colophon = strings["colophon"]
    lang = strings["lang"]
    try:
        version = Version.from_git().serialize(style=Style.Pep440)
    except RuntimeError:
        version = VERSION_FILE.read_text().strip()

    all_md = sorted(CONTENT_DIR.glob("*.md"))
    front_matter = [f for f in all_md if f.name.startswith("00-")]
    excluded = {"index.md", "license.md", "about-author.md"}
    chapter_files = [f for f in all_md if not f.name.startswith("00-") and f.name not in excluded]

    if not chapter_files and not front_matter:
        print("No content files found in xarter/")
        return

    for f in front_matter:
        print(f"  front matter: {f.name}")
    print(f"Found {len(chapter_files)} chapters:")
    for f in chapter_files:
        print(f"  - {f.name}")

    build_index(doc_strings, strings, strings.get("site", {}), doc["repo"], front_matter, chapter_files)

    content_files = [*front_matter, *chapter_files, CONFIG_FILE, STRINGS_FILE]
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

    # Display page numbers from here (counter has been running since prefaci)
    parts.append('#set page(numbering: "1", number-align: center)')
    parts.append("")

    for chapter_file in chapter_files:
        rel_path = chapter_file.relative_to(ROOT)
        parts.append(f"// Source: {rel_path}")
        parts.append(f'#render(read("../{rel_path}"), h1-level: 1)')
        parts.append("")

    # Appendix
    appendix_title = escape_typst(strings.get("appendix", {}).get("title", "Annex"))
    parts.append(f'#{{ set heading(numbering: "A.1.")')
    parts.append(f'   counter(heading).update(0)')
    license_title = escape_typst(strings.get("appendix", {}).get("license_title", "Llicència"))
    parts.append(f'   heading(level: 1)[{appendix_title}]')
    parts.append(f'   heading(level: 2)[{license_title}]')
    license_file = CONTENT_DIR / "license.md"
    license_path = f"../{license_file.relative_to(ROOT)}" if license_file.exists() else "../LICENSE"
    parts.append(f'   render(read("{license_path}"), h1-level: 3)')
    # About the author
    about_author_file = CONTENT_DIR / "about-author.md"
    if about_author_file.exists():
        about_title = escape_typst(strings.get("appendix", {}).get("about_author_title", "Sobre l'autor"))
        rel_path = f"../{about_author_file.relative_to(ROOT)}"
        parts.append(f'   heading(level: 2)[{about_title}]')
        parts.append(f'   render(read("{rel_path}"), h1-level: 3)')
        parts.append("")
    # Contributors
    if AUTHORS_FILE.exists():
        contributors_title = escape_typst(strings.get("appendix", {}).get("contributors_title", "Contribuïdors"))
        parts.append(f'   heading(level: 2)[{contributors_title}]')
        for line in AUTHORS_FILE.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            # Parse "Name <url>" format
            author_match = re.match(r"^(.+?)\s+<(.+?)>\s*$", line)
            if author_match:
                name = escape_typst(author_match.group(1))
                url = escape_typst(author_match.group(2))
                parts.append(f'   [- #link("{url}")[{name}]]')
            else:
                parts.append(f"   [- {escape_typst(line)}]")
        parts.append("")
    if CHANGELOG_FILE.exists():
        changelog_title = escape_typst(changelog["title"])
        changelog_intro = escape_typst(changelog.get("intro", ""))
        version_label = escape_typst(changelog.get("version_label", "Versió"))
        versions = parse_changelog(CHANGELOG_FILE)
        parts.append(f'   heading(level: 2)[{changelog_title}]')
        if changelog_intro:
            parts.append(f"   [{changelog_intro}]")
            parts.append("")
        parts.extend(changelog_to_typst(versions, version_label))
    parts.append("}")
    parts.append("")

    # Colophon (unnumbered, in TOC)
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
    parts.append(f"  #v(1.5em)")
    parts.append('  #text(size: 8pt, fill: rgb("#999"))[CC BY-SA 4.0]')
    parts.append("]")
    parts.append("#v(1fr)")
    parts.append("")

    BUILD_DIR.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text("\n".join(parts))
    print(f"Written {OUTPUT_FILE}")


if __name__ == "__main__":
    build()
