# ABOUTME: Document generation logic for the NextCat pipeline.
# ABOUTME: Typst document generation, index/nav generation, changelog parsing.

import re
import tomllib
from datetime import datetime, timezone
from pathlib import Path

from babel.dates import format_date
from dunamai import Style, Version

ROOT = Path.cwd()
CANONICAL_DIR = ROOT / "book"
TRANSLATIONS_DIR = CANONICAL_DIR / "translations"
CONFIG_FILE = ROOT / "config.toml"
VERSION_FILE = ROOT / "VERSION"
AUTHORS_FILE = ROOT / "AUTHORS"
CHANGELOG_FILE = ROOT / "CHANGELOG.md"
BUILD_DIR = ROOT / "build"
EXCLUDED_MD = {"index.md", "license.md", "about-author.md", "changelog.md", "contributing.md", "conceptes-clau.md"}


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

    front_matter = []
    for f in canonical_fm:
        translated = content_dir / f.name
        front_matter.append(translated if translated.exists() else f)

    chapters = []
    for f in canonical_ch:
        translated = content_dir / f.name
        chapters.append(translated if translated.exists() else f)

    return front_matter, chapters


def _typst_param(key: str, value: str) -> str:
    """Format a Typst named parameter with an escaped string value."""
    return f'  {key}: "{escape_typst(value)}",'


def build_typst(
    content_dir: Path,
    strings: dict,
    config: dict,
    version: str,
    front_matter: list[Path],
    chapter_files: list[Path],
    translation_notice: str = "",
    *,
    include_changelog: bool = True,
    variant_suffix: str = "",
) -> Path:
    """Generate a Typst document for one language. Returns the .typ file path."""
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
        _typst_param("title", doc_strings["title"]),
        _typst_param("subtitle", doc_strings["subtitle"]),
        _typst_param("author", doc["author"]),
        _typst_param("email", doc["email"]),
        _typst_param("lang", lang),
        _typst_param("toc-title", toc["title"]),
        _typst_param("version", version),
        _typst_param("version-label", title_page.get("version_label", "Versió")),
        _typst_param("cover-date", cover_date(lang)),
        _typst_param("url", doc["url"]),
        _typst_param("repo", doc["repo"]),
        _typst_param("generated-text", generated_text),
        _typst_param("modified-text", modified_text),
        _typst_param("modified-label", title_page["modified"]),
        _typst_param("generated-label", title_page["generated"]),
        _typst_param("translation-notice", translation_notice),
        ")",
        "",
    ]

    toc_title = escape_typst(toc["title"])
    parts.append("// TOC (custom layout: numbered rows for chapters, lettered rows for annex)")
    parts.append("#page(numbering: none)[")
    parts.append("  #show link: it => it.body")
    parts.append("  #v(1.5cm)")
    parts.append("  #align(center)[")
    parts.append(
        f'    #text(size: 20pt, weight: "bold", tracking: 0.12em, hyphenate: false)[#smallcaps([{toc_title}])]'
    )
    parts.append("  ]")
    parts.append("  #v(2.5em)")
    parts.append("  #context {")
    parts.append("    let fm = query(heading.where(level: 2).before(<tg-main-start>))")
    parts.append(
        "    let chs = query(heading.where(level: 1).after(<tg-main-start>).before(<tg-annex-start>))"
    )
    parts.append(
        "    let annex = query(heading.where(level: 1).after(<tg-annex-start>).before(<tg-colo-start>))"
    )
    parts.append(
        "    let subs = query(heading.where(level: 2).after(<tg-annex-start>).before(<tg-colo-start>))"
    )
    parts.append("    let colo = query(heading.where(level: 1).after(<tg-colo-start>))")
    parts.append("")
    parts.append('    let num(s) = text(fill: rgb("#555"))[#s]')
    parts.append("    let row(n, body, loc) = (num(n), link(loc)[#body])")
    parts.append("")
    parts.append("    let rows = ()")
    parts.append("    let i = 0")
    parts.append("    for h in fm {")
    parts.append('      rows += row(str(i) + ".", h.body, h.location())')
    parts.append("      i += 1")
    parts.append("    }")
    parts.append("    for h in chs {")
    parts.append('      rows += row(str(i) + ".", h.body, h.location())')
    parts.append("      i += 1")
    parts.append("    }")
    parts.append("")
    parts.append("    grid(")
    parts.append("      columns: (2.5em, 1fr),")
    parts.append("      column-gutter: 0.4em,")
    parts.append("      row-gutter: 1em,")
    parts.append("      ..rows,")
    parts.append("    )")
    parts.append("")
    parts.append("    if annex.len() > 0 {")
    parts.append("      v(1.6em)")
    parts.append(
        '      link(annex.at(0).location())[#text(fill: rgb("#777"))[#annex.at(0).body]]'
    )
    parts.append("      v(1em)")
    parts.append("")
    parts.append("      let sub-rows = ()")
    parts.append("      let j = 1")
    parts.append("      for h in subs {")
    parts.append('        sub-rows += row(numbering("A.", j), h.body, h.location())')
    parts.append("        j += 1")
    parts.append("      }")
    parts.append("      grid(")
    parts.append("        columns: (2.5em, 1fr),")
    parts.append("        column-gutter: 0.4em,")
    parts.append("        row-gutter: 1em,")
    parts.append("        ..sub-rows,")
    parts.append("      )")
    parts.append("    }")
    parts.append("")
    parts.append("    if colo.len() > 0 {")
    parts.append("      v(1.6em)")
    parts.append("      link(colo.at(0).location())[#colo.at(0).body]")
    parts.append("    }")
    parts.append("  }")
    parts.append("]")
    parts.append("")
    parts.append('#set page(numbering: "1", number-align: center)')
    parts.append("#counter(page).update(1)")
    parts.append("")

    if front_matter:
        parts.append("// Front matter (unnumbered)")
        parts.append("#{ set heading(numbering: none, outlined: false)")
        for fm_file in front_matter:
            rel_path = fm_file.relative_to(ROOT)
            parts.append(f'   render(read("../{rel_path}"), h1-level: 2)')
        parts.append("}")
        parts.append("")

    parts.append("#[#metadata(none) <tg-main-start>]")
    parts.append("")

    for chapter_file in chapter_files:
        rel_path = chapter_file.relative_to(ROOT)
        parts.append(f"// Source: {rel_path}")
        parts.append(f'#render(read("../{rel_path}"), h1-level: 1)')
        parts.append("")

    # Appendix
    appendix = strings.get("appendix", {})
    appendix_title = escape_typst(appendix.get("title", "Annex"))
    parts.append("#[#metadata(none) <tg-annex-start>]")
    parts.append("#{ set heading(numbering: (..nums) => {")
    parts.append("     let n = nums.pos()")
    parts.append('     if n.len() == 1 { return [] }')
    parts.append('     numbering("A.1.", ..n.slice(1))')
    parts.append("   })")
    parts.append("   counter(heading).update(0)")
    license_title = escape_typst(appendix.get("license_title", "Llicència"))
    parts.append(f'   heading(level: 1, numbering: none)[{appendix_title}]')
    parts.append(f'   heading(level: 2)[{license_title}]')
    license_file = content_dir / "license.md"
    license_path = f"../{license_file.relative_to(ROOT)}" if license_file.exists() else "../LICENSE"
    parts.append(f'   render(read("{license_path}"), h1-level: 3)')

    concepts_file = content_dir / "conceptes-clau.md"
    if not concepts_file.exists():
        concepts_file = CANONICAL_DIR / "conceptes-clau.md"
    if concepts_file.exists():
        concepts_title = escape_typst(appendix.get("concepts_title", "Conceptes clau per a lectors no tècnics"))
        rel_path = f"../{concepts_file.relative_to(ROOT)}"
        parts.append(f'   heading(level: 2)[{concepts_title}]')
        parts.append(f'   render(read("{rel_path}"), h1-level: 3)')
        parts.append("")

    about_author_file = content_dir / "about-author.md"
    if not about_author_file.exists():
        about_author_file = CANONICAL_DIR / "about-author.md"
    if about_author_file.exists():
        about_title = escape_typst(appendix.get("about_author_title", "Sobre l'autor"))
        rel_path = f"../{about_author_file.relative_to(ROOT)}"
        parts.append(f'   heading(level: 2)[{about_title}]')
        parts.append(f'   render(read("{rel_path}"), h1-level: 3)')
        parts.append("")

    # Contributing
    contributing_title = appendix.get("contributing_title")
    contributing_text = appendix.get("contributing_text")
    if contributing_title and contributing_text:
        formatted = contributing_text.format(repo=doc["repo"])
        parts.append(f'   heading(level: 2)[{escape_typst(contributing_title)}]')
        parts.append(f'   render("{escape_typst(formatted)}")')
        parts.append("")

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

    if include_changelog and CHANGELOG_FILE.exists():
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
    parts.append("#[#metadata(none) <tg-colo-start>]")
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
    output_file = BUILD_DIR / f"document.{lang}{variant_suffix}.typ"
    output_file.write_text("\n".join(parts))
    return output_file
