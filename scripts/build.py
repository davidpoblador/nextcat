# ABOUTME: Generates a Typst document that renders markdown chapters via cmarker.
# ABOUTME: Reads config, strings, and chapters from xarter/, writes document.typ.

import re
import tomllib
from datetime import datetime, timezone
from pathlib import Path

from dunamai import Style, Version

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "xarter"
CONFIG_FILE = CONTENT_DIR / "config.toml"
STRINGS_FILE = CONTENT_DIR / "strings.toml"
VERSION_FILE = ROOT / "VERSION"
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


def last_modified_date(files: list[Path]) -> str:
    """Most recent filesystem mtime across the given files."""
    mtimes = [f.stat().st_mtime for f in files if f.exists()]
    if not mtimes:
        return "-"
    dt = datetime.fromtimestamp(max(mtimes), tz=timezone.utc)
    return dt.strftime("%d/%m/%Y %H:%M")


def generation_date() -> str:
    """Current timestamp formatted for display."""
    return datetime.now(tz=timezone.utc).strftime("%d/%m/%Y %H:%M UTC")


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
        # List items: * text ([hash](url)) or * text (hash)
        item_match = re.match(r"^\*\s+(.+?)(?:\s+\(\[?[a-f0-9]+\]?\(?[^)]*\)?\))?$", line)
        if item_match:
            text = item_match.group(1)
            # Strip trailing markdown links
            text = re.sub(r"\s*\(\[[a-f0-9]+\]\([^)]+\)\)\s*$", "", text)
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
            lines.append(f"   [- {escape_typst(item)}]")
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
    site: dict,
    repo: str,
    front_matter: list[Path],
    chapter_files: list[Path],
) -> None:
    """Generate the mkdocs index.md from chapter files and strings."""
    lines = [
        f"# {doc_strings['title']}",
        "",
        f"**{doc_strings['subtitle']}**",
        "",
    ]

    for fm in front_matter:
        lines.append(f"- [{chapter_title(fm)}]({fm.name})")
    for ch in chapter_files:
        lines.append(f"- [{chapter_title(ch)}]({ch.name})")
    lines.append("")

    lines.append(f"## {site['downloads']}")
    lines.append("")
    lines.append(site["downloads_text"].format(repo=repo))
    lines.append("")

    lines.append(f"## {site['license']}")
    lines.append("")
    lines.append(site["license_text"])
    lines.append("")

    INDEX_FILE.write_text("\n".join(lines))
    print(f"Written {INDEX_FILE}")


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
    excluded = {"index.md", "license.md"}
    chapter_files = [f for f in all_md if not f.name.startswith("00-") and f.name not in excluded]

    if not chapter_files and not front_matter:
        print("No content files found in xarter/")
        return

    for f in front_matter:
        print(f"  front matter: {f.name}")
    print(f"Found {len(chapter_files)} chapters:")
    for f in chapter_files:
        print(f"  - {f.name}")

    build_index(doc_strings, strings.get("site", {}), doc["repo"], front_matter, chapter_files)

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
        typst_param("repo", doc["repo"]),
        typst_param("generated-text", generated_text),
        typst_param("modified-text", modified_text),
        typst_param("colophon-title", colophon["title"]),
        typst_param("colophon-text", colophon["text"]),
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

    # Page numbering starts after TOC
    parts.append('#set page(numbering: "1", number-align: center)')
    parts.append("#counter(page).update(1)")
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

    BUILD_DIR.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text("\n".join(parts))
    print(f"Written {OUTPUT_FILE}")


if __name__ == "__main__":
    build()
