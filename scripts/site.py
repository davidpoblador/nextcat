# ABOUTME: Static HTML reader for the NextCat book.
# ABOUTME: Renders markdown chapters to a LaTeX-styled HTML site under public/.

import re
import shutil
from dataclasses import dataclass
from pathlib import Path

import markdown
import typer
from jinja2 import Environment, FileSystemLoader, select_autoescape
from rich.console import Console

from scripts.generate import (
    AUTHORS_FILE,
    CANONICAL_DIR,
    CHANGELOG_FILE,
    CONFIG_FILE,
    ROOT,
    chapter_title,
    cover_date,
    get_version,
    load_toml,
    resolve_chapters,
)

PUBLIC_DIR = ROOT / "public"
SITE_TEMPLATES = ROOT / "templates" / "site"
FONTS_DIR = ROOT / "fonts"

app = typer.Typer(help="Build the NextCat HTML reader.")
console = Console()


@dataclass
class Page:
    href: str
    title: str
    source: Path | None
    number: int | None = None


_LEADING_H1 = re.compile(r"\A\s*#\s+[^\n]+\n+", re.MULTILINE)


def _render_markdown(md_text: str, strip_leading_h1: bool = True) -> str:
    if strip_leading_h1:
        md_text = _LEADING_H1.sub("", md_text, count=1)
    return markdown.markdown(
        md_text,
        extensions=["extra", "sane_lists", "smarty"],
        output_format="html5",
    )


def _slug(path: Path) -> str:
    stem = path.stem
    # Strip the leading "NN-" chapter prefix for friendlier URLs.
    if len(stem) > 3 and stem[:2].isdigit() and stem[2] == "-":
        return stem[3:]
    return stem


@app.command()
def build() -> None:
    """Generate the HTML reader into public/."""
    config = load_toml(CONFIG_FILE)
    strings = load_toml(CANONICAL_DIR / "strings.toml")
    version = get_version()
    lang = strings["lang"]
    doc = strings["document"]
    title_page = strings["title_page"]
    appendix_strings = strings.get("appendix", {})
    toc_strings = strings["toc"]
    changelog_strings = strings.get("changelog", {})
    chapter_label = toc_strings.get("chapter_label", "Capítol")

    front_matter_files, chapter_files = resolve_chapters(CANONICAL_DIR, CANONICAL_DIR)

    env = Environment(
        loader=FileSystemLoader(SITE_TEMPLATES),
        autoescape=select_autoescape(["html"]),
    )

    if PUBLIC_DIR.exists():
        shutil.rmtree(PUBLIC_DIR)
    PUBLIC_DIR.mkdir(parents=True)

    # Copy assets
    shutil.copy(SITE_TEMPLATES / "style.css", PUBLIC_DIR / "style.css")
    public_fonts = PUBLIC_DIR / "fonts"
    public_fonts.mkdir()
    for otf in FONTS_DIR.glob("*.otf"):
        shutil.copy(otf, public_fonts / otf.name)

    # Build page list
    front_pages: list[Page] = [
        Page(href=f"{_slug(p)}.html", title=chapter_title(p), source=p)
        for p in front_matter_files
    ]
    chapter_pages: list[Page] = [
        Page(href=f"{_slug(p)}.html", title=chapter_title(p), source=p, number=i + 1)
        for i, p in enumerate(chapter_files)
    ]

    # Synthetic appendix pages (license, authors, changelog)
    appendix_pages: list[Page] = []
    license_file = CANONICAL_DIR / "license.md"
    if license_file.exists():
        appendix_pages.append(
            Page(
                href="license.html",
                title=appendix_strings.get("license_title", "Llicència"),
                source=license_file,
            )
        )
    about_file = CANONICAL_DIR / "about-author.md"
    if about_file.exists():
        appendix_pages.append(
            Page(
                href="about-author.html",
                title=appendix_strings.get("about_author_title", "Sobre l'autor"),
                source=about_file,
            )
        )
    if AUTHORS_FILE.exists():
        appendix_pages.append(
            Page(
                href="contributors.html",
                title=appendix_strings.get("contributors_title", "Contribuïdors"),
                source=None,
            )
        )
    if CHANGELOG_FILE.exists():
        appendix_pages.append(
            Page(
                href="changelog.html",
                title=changelog_strings.get("title", "Registre de canvis"),
                source=CHANGELOG_FILE,
            )
        )

    all_pages = front_pages + chapter_pages + appendix_pages

    def neighbours(idx: int) -> tuple[Page | None, Page | None]:
        prev_p = all_pages[idx - 1] if idx > 0 else None
        next_p = all_pages[idx + 1] if idx + 1 < len(all_pages) else None
        return prev_p, next_p

    # Index
    index_html = env.get_template("index.html").render(
        lang=lang,
        page_title=doc["title"],
        title=doc["title"],
        subtitle=doc["subtitle"],
        author=config["document"]["author"],
        version=version,
        version_label=title_page.get("version_label", "Versió"),
        cover_date=cover_date(lang),
        toc_title=toc_strings["title"],
        front_matter=[{"href": p.href, "title": p.title} for p in front_pages],
        chapters=[{"href": p.href, "title": p.title} for p in chapter_pages],
        appendix=[{"href": p.href, "title": p.title} for p in appendix_pages],
        assets="",
    )
    (PUBLIC_DIR / "index.html").write_text(index_html)
    console.print(f"  [dim]→[/dim] public/index.html")

    # Chapter pages
    chapter_template = env.get_template("chapter.html")
    for idx, page in enumerate(all_pages):
        prev_p, next_p = neighbours(idx)
        if page.source is not None and page.source.suffix == ".md":
            body_html = _render_markdown(page.source.read_text())
        else:
            body_html = _synthetic_body(page, changelog_strings)

        html = chapter_template.render(
            lang=lang,
            page_title=f"{page.title} — {doc['title']}",
            title=page.title,
            chapter_number=page.number,
            chapter_label=chapter_label,
            body_html=body_html,
            body_class="chapter-body" if page.number else "front-body",
            prev={"href": prev_p.href, "title": prev_p.title} if prev_p else None,
            next={"href": next_p.href, "title": next_p.title} if next_p else None,
            toc_title=toc_strings["title"],
            assets="",
        )
        (PUBLIC_DIR / page.href).write_text(html)
        console.print(f"  [dim]→[/dim] public/{page.href}")

    console.print(f"\n[green bold]Done.[/green bold] Open [cyan]file://{PUBLIC_DIR}/index.html[/cyan]")


def _synthetic_body(page: Page, changelog_strings: dict) -> str:
    """Render pages that aren't plain markdown (contributors list, changelog)."""
    if page.href == "contributors.html":
        items = []
        import re as _re
        for line in AUTHORS_FILE.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            m = _re.match(r"^(.+?)\s+<(.+?)>\s*$", line)
            if m:
                items.append(f'<li><a href="{m.group(2)}">{m.group(1)}</a></li>')
            else:
                items.append(f"<li>{line}</li>")
        return "<ul>\n" + "\n".join(items) + "\n</ul>"

    if page.href == "changelog.html":
        intro = changelog_strings.get("intro", "")
        body = _render_markdown(CHANGELOG_FILE.read_text())
        return (f"<p>{intro}</p>\n" if intro else "") + body

    return ""


if __name__ == "__main__":
    app()
