# ABOUTME: EPUB builder for the NextCat book.
# ABOUTME: Renders the same Markdown sources used by the PDF/HTML pipelines into an EPUB3.

import re
from dataclasses import dataclass
from pathlib import Path

import markdown
import resvg_py
import typer
from ebooklib import epub
from jinja2 import Environment, FileSystemLoader, select_autoescape
from rich.console import Console

from scripts.generate import (
    AUTHORS_FILE,
    BUILD_DIR,
    CANONICAL_DIR,
    CHANGELOG_FILE,
    CONFIG_FILE,
    ROOT,
    chapter_title,
    cover_date,
    generation_date,
    get_version,
    last_modified_date,
    load_toml,
    parse_changelog,
    resolve_chapters,
)

FONTS_DIR = ROOT / "fonts"
EPUB_TEMPLATES = ROOT / "templates" / "epub"

# Mirrors scripts/build.py: reader edition ("", no changelog) and archival "-full"
VARIANTS: list[tuple[str, bool]] = [
    ("", False),
    ("-full", True),
]

app = typer.Typer(help="Build the NextCat EPUB editions.")
console = Console()


@dataclass
class Section:
    file_name: str
    title: str
    body_html: str
    body_class: str
    display_title: str | None = None  # used for chapter-head prefix
    chapter_number: int | None = None
    chapter_label: str | None = None
    include_in_nav: bool = True
    nav_group: str | None = None  # if set, groups sibling entries under a nav heading


_LEADING_H1 = re.compile(r"\A\s*#\s+[^\n]+\n+", re.MULTILINE)


def _md_to_html(md_text: str, strip_leading_h1: bool = True) -> str:
    if strip_leading_h1:
        md_text = _LEADING_H1.sub("", md_text, count=1)
    return markdown.markdown(
        md_text,
        extensions=["extra", "sane_lists", "smarty"],
        output_format="html5",
    )


def _wrap_body(section: Section) -> str:
    head_parts: list[str] = []
    if section.display_title:
        head_parts.append('<div class="chapter-head">')
        if section.chapter_label and section.chapter_number is not None:
            head_parts.append(
                f'  <div class="chapnum">{section.chapter_label} {section.chapter_number}</div>'
            )
        head_parts.append(f'  <h1>{section.display_title}</h1>')
        head_parts.append('</div>')
    head = "\n".join(head_parts)
    return (
        f'<div class="{section.body_class}">\n'
        f'{head}\n{section.body_html}\n</div>'
    )


def _contributors_body() -> str:
    items = []
    for line in AUTHORS_FILE.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^(.+?)\s+<(.+?)>\s*$", line)
        if m:
            items.append(f'<li><a href="{m.group(2)}">{m.group(1)}</a></li>')
        else:
            items.append(f"<li>{line}</li>")
    return "<ul>\n" + "\n".join(items) + "\n</ul>"


def _changelog_body(intro: str, version_label: str) -> str:
    versions = parse_changelog(CHANGELOG_FILE)
    parts: list[str] = ['<div class="changelog">']
    if intro:
        parts.append(f'<p>{intro}</p>')
    for ver, items in versions:
        parts.append(f'<h3>{version_label} {ver}</h3>')
        parts.append('<ul>')
        for item in items:
            parts.append(f'  <li>{item}</li>')
        parts.append('</ul>')
    parts.append('</div>')
    return "\n".join(parts)


def _colophon_body(config: dict, version: str, strings: dict, modified_text: str) -> str:
    doc = config["document"]
    colophon = strings.get("colophon", {})
    title_page = strings["title_page"]
    version_label = title_page.get("version_label", "Versió")
    modified_label = title_page["modified"]
    generated_label = title_page["generated"]
    text = colophon.get("text", "")
    return (
        f'<div class="colophon">\n'
        f'  <h1>{colophon.get("title", "Colofó")}</h1>\n'
        f'  <p class="colophon-text">{text}</p>\n'
        f'  <p>{version_label}: {version}</p>\n'
        f'  <p>{modified_label}: {modified_text}<br/>\n'
        f'  {generated_label}: {generation_date()}</p>\n'
        f'  <p><a href="{doc["url"]}">{doc["url"]}</a><br/>\n'
        f'  <a href="mailto:{doc["email"]}">{doc["email"]}</a></p>\n'
        f'  <p><a href="{doc["repo"]}">{doc["repo"]}</a></p>\n'
        f'  <p class="colophon-license">CC BY-SA 4.0</p>\n'
        f'</div>\n'
    )


# Catalan function words that should not orphan at line ends on the cover.
# Keeps the typographic feel of the Typst cover's stick-short rule.
_COVER_STICK_WORDS = {
    "de", "a", "i", "la", "el", "els", "les", "al", "als",
    "del", "dels", "per", "en",
}


def _wrap_cover_lines(text: str, budget: int) -> list[str]:
    """Greedy word wrap; then pull trailing stick-words onto the next line."""
    words = text.split()
    lines: list[list[str]] = [[]]
    for w in words:
        candidate = " ".join([*lines[-1], w])
        if lines[-1] and len(candidate) > budget:
            lines.append([w])
        else:
            lines[-1].append(w)
    # Avoid a short function word ending any line but the last.
    for i in range(len(lines) - 1):
        while len(lines[i]) > 1 and lines[i][-1].lower() in _COVER_STICK_WORDS:
            moved = lines[i].pop()
            lines[i + 1].insert(0, moved)
    return [" ".join(words) for words in lines]


def _render_cover_png(strings: dict, config: dict, version: str, lang: str) -> bytes:
    """Render the cover SVG template and rasterize it to a PNG via resvg."""
    doc = strings["document"]
    title_lines = _wrap_cover_lines(doc["title"], budget=24)
    subtitle_lines = _wrap_cover_lines(doc["subtitle"], budget=34)

    title_y = 880
    subtitle_y = title_y + (len(title_lines) - 1) * 132 + 160

    env = Environment(
        loader=FileSystemLoader(EPUB_TEMPLATES),
        autoescape=select_autoescape(["svg", "xml"]),
    )
    svg = env.get_template("cover.svg").render(
        title_lines=title_lines,
        subtitle_lines=subtitle_lines,
        title_y=title_y,
        subtitle_y=subtitle_y,
        author=config["document"]["author"],
        cover_date=cover_date(lang),
        version=version,
    )

    return bytes(resvg_py.svg_to_bytes(
        svg_string=svg,
        font_dirs=[str(FONTS_DIR)],
        skip_system_fonts=True,
        width=1600,
        height=2560,
    ))


def _metadata_body(strings: dict, config: dict, version: str, modified_text: str) -> str:
    """Imprint page — mirrors the PDF's metadata verso before the TOC."""
    doc = strings["document"]
    title_page = strings["title_page"]
    version_label = title_page.get("version_label", "Versió")
    modified_label = title_page["modified"]
    generated_label = title_page["generated"]
    cfg = config["document"]
    return (
        f'<div class="imprint">\n'
        f'  <p class="imprint-title"><strong>{doc["title"]}</strong><br/>\n'
        f'  <span class="imprint-subtitle">{doc["subtitle"]}</span></p>\n'
        f'  <p>{version_label}: {version}</p>\n'
        f'  <p>{modified_label}: {modified_text}<br/>\n'
        f'  {generated_label}: {generation_date()}</p>\n'
        f'  <p><a href="{cfg["url"]}">{cfg["url"]}</a><br/>\n'
        f'  <a href="mailto:{cfg["email"]}">{cfg["email"]}</a></p>\n'
        f'  <p><a href="{cfg["repo"]}">{cfg["repo"]}</a></p>\n'
        f'  <p class="imprint-license">CC BY-SA 4.0</p>\n'
        f'</div>\n'
    )


def _build_one(
    *,
    config: dict,
    strings: dict,
    version: str,
    include_changelog: bool,
    variant_suffix: str,
) -> Path:
    """Build a single EPUB variant and return the path."""
    lang = strings["lang"]
    doc = strings["document"]
    appendix_strings = strings.get("appendix", {})
    toc_strings = strings["toc"]
    changelog_strings = strings.get("changelog", {})
    chapter_label = toc_strings.get("chapter_label", "Capítol")

    front_matter_files, chapter_files = resolve_chapters(CANONICAL_DIR, CANONICAL_DIR)
    modified_text = last_modified_date(
        chapter_files + front_matter_files + [CONFIG_FILE]
    )

    book = epub.EpubBook()
    book.set_identifier(f'nextcat-{lang}{variant_suffix}-{version}')
    book.set_title(doc["title"])
    book.set_language(lang)
    book.add_author(config["document"]["author"])
    book.add_metadata("DC", "description", doc["subtitle"])
    book.add_metadata("DC", "publisher", config["document"]["url"])
    book.add_metadata("DC", "rights", "CC BY-SA 4.0")

    # Stylesheet
    css = epub.EpubItem(
        uid="style",
        file_name="style.css",
        media_type="text/css",
        content=(EPUB_TEMPLATES / "style.css").read_bytes(),
    )
    book.add_item(css)

    # Fonts (embedded — Libertinus Serif, SIL OFL). The CSS references
    # ../fonts/<name>.otf relative to the stylesheet inside OEBPS/.
    for otf in sorted(FONTS_DIR.glob("*.otf")):
        book.add_item(
            epub.EpubItem(
                uid=f"font-{otf.stem.lower()}",
                file_name=f"fonts/{otf.name}",
                media_type="font/otf",
                content=otf.read_bytes(),
            )
        )

    # Cover image — rendered from templates/epub/cover.svg via resvg. ebooklib
    # creates the cover.xhtml page automatically and wires up the cover-image
    # metadata so library thumbnails (Apple Books, Calibre, …) pick it up.
    book.set_cover("cover.png", _render_cover_png(strings, config, version, lang))

    # Build the list of sections, in spine order.
    sections: list[Section] = []

    # 1. Imprint / metadata page (mirrors the PDF's metadata verso before the TOC)
    sections.append(Section(
        file_name="imprint.xhtml",
        title=doc["title"],
        body_html=_metadata_body(strings, config, version, modified_text),
        body_class="imprint-body",
        include_in_nav=False,
    ))

    # 3. Front matter
    for p in front_matter_files:
        t = chapter_title(p)
        sections.append(Section(
            file_name=f"{p.stem}.xhtml",
            title=t,
            body_html=_md_to_html(p.read_text()),
            body_class="front-body",
            display_title=t,
        ))

    # 3. Chapters
    for i, p in enumerate(chapter_files, start=1):
        t = chapter_title(p)
        sections.append(Section(
            file_name=f"{p.stem}.xhtml",
            title=t,
            body_html=_md_to_html(p.read_text()),
            body_class="chapter-body",
            display_title=t,
            chapter_number=i,
            chapter_label=chapter_label,
        ))

    # 4. Annex — introduced by a dedicated title page, then one subsection per item
    annex_title = appendix_strings.get("title", "Annex")
    annex_intro_file = "annex.xhtml"
    sections.append(Section(
        file_name=annex_intro_file,
        title=annex_title,
        body_html=f'<div class="annex-intro"><h1>{annex_title}</h1></div>',
        body_class="annex-intro-body",
    ))

    license_file = CANONICAL_DIR / "license.md"
    if license_file.exists():
        t = appendix_strings.get("license_title", "Llicència")
        sections.append(Section(
            file_name="annex-license.xhtml",
            title=t,
            body_html=_md_to_html(license_file.read_text()),
            body_class="annex-body",
            display_title=t,
            nav_group=annex_title,
        ))
    concepts_file = CANONICAL_DIR / "conceptes-clau.md"
    if concepts_file.exists():
        t = appendix_strings.get("concepts_title", "Conceptes clau per a lectors no tècnics")
        sections.append(Section(
            file_name="annex-concepts.xhtml",
            title=t,
            body_html=_md_to_html(concepts_file.read_text()),
            body_class="annex-body",
            display_title=t,
            nav_group=annex_title,
        ))
    about_file = CANONICAL_DIR / "about-author.md"
    if about_file.exists():
        t = appendix_strings.get("about_author_title", "Sobre l'autor")
        sections.append(Section(
            file_name="annex-about.xhtml",
            title=t,
            body_html=_md_to_html(about_file.read_text()),
            body_class="annex-body",
            display_title=t,
            nav_group=annex_title,
        ))
    if appendix_strings.get("contributing_title") and appendix_strings.get("contributing_text"):
        raw = appendix_strings["contributing_text"].format(repo=config["document"]["repo"])
        sections.append(Section(
            file_name="annex-contributing.xhtml",
            title=appendix_strings["contributing_title"],
            body_html=_md_to_html(raw, strip_leading_h1=False),
            body_class="annex-body",
            display_title=appendix_strings["contributing_title"],
            nav_group=annex_title,
        ))
    if AUTHORS_FILE.exists():
        t = appendix_strings.get("contributors_title", "Contribuïdors")
        sections.append(Section(
            file_name="annex-contributors.xhtml",
            title=t,
            body_html=_contributors_body(),
            body_class="annex-body",
            display_title=t,
            nav_group=annex_title,
        ))
    if include_changelog and CHANGELOG_FILE.exists():
        t = changelog_strings.get("title", "Registre de canvis")
        sections.append(Section(
            file_name="annex-changelog.xhtml",
            title=t,
            body_html=_changelog_body(
                changelog_strings.get("intro", ""),
                changelog_strings.get("version_label", "Versió"),
            ),
            body_class="annex-body",
            display_title=t,
            nav_group=annex_title,
        ))

    # 5. Colophon
    sections.append(Section(
        file_name="colophon.xhtml",
        title=strings.get("colophon", {}).get("title", "Colofó"),
        body_html=_colophon_body(config, version, strings, modified_text),
        body_class="colophon-body",
    ))

    # Materialise each section as an EpubHtml and add to spine + nav.
    chapters: list[epub.EpubHtml] = []
    for sec in sections:
        body = _wrap_body(sec) if sec.display_title else sec.body_html
        item = epub.EpubHtml(
            title=sec.title,
            file_name=sec.file_name,
            lang=lang,
            content=body,
        )
        item.add_link(rel="stylesheet", type="text/css", href="style.css")
        book.add_item(item)
        chapters.append(item)

    # Nested TOC: any section with nav_group=annex_title is nested under the
    # annex intro (file annex.xhtml), so the reader shows "Annex > Llicència, …"
    # instead of a flat list starting with "Annex: Llicència".
    toc_entries: list = []
    annex_children: list = []
    annex_parent: epub.EpubHtml | None = None
    for chap, sec in zip(chapters, sections, strict=True):
        if not sec.include_in_nav:
            continue
        if sec.file_name == annex_intro_file:
            annex_parent = chap
        elif sec.nav_group == annex_title:
            annex_children.append(
                epub.Link(chap.file_name, sec.title, f"toc-{chap.id}")
            )
        else:
            toc_entries.append(chap)
    if annex_parent is not None:
        annex_link = epub.Link(annex_parent.file_name, annex_title, f"toc-{annex_parent.id}")
        # Colophon sits after the annex in the reading order — preserve that by
        # inserting the annex group just before the colophon (last entry).
        colophon_entry = toc_entries.pop() if toc_entries else None
        toc_entries.append((annex_link, annex_children))
        if colophon_entry is not None:
            toc_entries.append(colophon_entry)

    book.toc = toc_entries
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Spine order mirrors the PDF: cover → imprint → nav (TOC) → front matter
    # → chapters → annex → colophon. "cover" is the auto-generated page that
    # set_cover attached; the nav document sits after the imprint to match the
    # PDF's "Continguts" page.
    imprint_index = next(
        i for i, s in enumerate(sections) if s.file_name == "imprint.xhtml"
    )
    head = chapters[: imprint_index + 1]
    tail = chapters[imprint_index + 1 :]
    book.spine = ["cover", *head, "nav", *tail]

    BUILD_DIR.mkdir(exist_ok=True)
    output_file = BUILD_DIR / f"nextcat-{version}.{lang}{variant_suffix}.epub"
    epub.write_epub(str(output_file), book, {"epub3_pages": False})
    console.print(f"  [green]✓[/green] [{lang}{variant_suffix}] {output_file.relative_to(ROOT)}")
    return output_file


@app.command()
def build() -> None:
    """Generate both EPUB editions (reader + full archival) into build/."""
    config = load_toml(CONFIG_FILE)
    strings = load_toml(CANONICAL_DIR / "strings.toml")
    version = get_version()
    lang = strings["lang"]
    console.print(f"[bold cyan][{lang}][/bold cyan] EPUB · {len(VARIANTS)} variants")
    for suffix, include_changelog in VARIANTS:
        _build_one(
            config=config,
            strings=strings,
            version=version,
            include_changelog=include_changelog,
            variant_suffix=suffix,
        )
    console.print("\n[green bold]Done.[/green bold]")


if __name__ == "__main__":
    app()
