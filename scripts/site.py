# ABOUTME: Static HTML reader for the NextCat book.
# ABOUTME: Renders markdown chapters to a LaTeX-styled HTML site under public/.

import hashlib
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
    generation_date,
    get_version,
    last_modified_date,
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
    kind: str | None = None


_LEADING_H1 = re.compile(r"\A\s*#\s+[^\n]+\n+", re.MULTILINE)


def _render_markdown(md_text: str, strip_leading_h1: bool = True) -> str:
    if strip_leading_h1:
        md_text = _LEADING_H1.sub("", md_text, count=1)
    return markdown.markdown(
        md_text,
        extensions=["extra", "sane_lists", "smarty"],
        output_format="html5",
    )


def _write_page(slug: str, html: str) -> None:
    """Write `html` so it's served at /{slug} (directory with index.html inside)."""
    target = PUBLIC_DIR / slug
    target.mkdir(parents=True, exist_ok=True)
    (target / "index.html").write_text(html)


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

    # Copy assets. The CSS gets a content-hash query string in the <link>
    # tag below so browsers re-fetch it when (and only when) it changes.
    css_source = SITE_TEMPLATES / "style.css"
    shutil.copy(css_source, PUBLIC_DIR / "style.css")
    css_version = hashlib.sha256(css_source.read_bytes()).hexdigest()[:10]
    public_fonts = PUBLIC_DIR / "fonts"
    public_fonts.mkdir()
    for otf in FONTS_DIR.glob("*.otf"):
        shutil.copy(otf, public_fonts / otf.name)

    # GitHub Pages custom domain
    cname_src = CANONICAL_DIR / "CNAME"
    if cname_src.exists():
        shutil.copy(cname_src, PUBLIC_DIR / "CNAME")

    # Stable, language-agnostic URL slugs:
    #   /cap0 .. /capN  — front matter + chapters (continuous TOC numbering)
    #   /annex1 .. /annexN — appendix items
    #   /colophon — colofó
    front_pages: list[Page] = []
    chapter_pages: list[Page] = []
    toc_index = 0
    for p in front_matter_files:
        front_pages.append(Page(href=f"/cap{toc_index}", title=chapter_title(p), source=p))
        toc_index += 1
    for i, p in enumerate(chapter_files):
        chapter_pages.append(
            Page(href=f"/cap{toc_index}", title=chapter_title(p), source=p, number=i + 1)
        )
        toc_index += 1

    # Appendix pages (order matches the PDF annex)
    appendix_specs: list[tuple[str, Path | None, str]] = []
    license_file = CANONICAL_DIR / "license.md"
    if license_file.exists():
        appendix_specs.append(("license", license_file, appendix_strings.get("license_title", "Llicència")))
    concepts_file = CANONICAL_DIR / "conceptes-clau.md"
    if concepts_file.exists():
        appendix_specs.append((
            "concepts",
            concepts_file,
            appendix_strings.get("concepts_title", "Conceptes clau per a lectors no tècnics"),
        ))
    about_file = CANONICAL_DIR / "about-author.md"
    if about_file.exists():
        appendix_specs.append(("about", about_file, appendix_strings.get("about_author_title", "Sobre l'autor")))
    if appendix_strings.get("contributing_title") and appendix_strings.get("contributing_text"):
        appendix_specs.append(("contributing", None, appendix_strings["contributing_title"]))
    if AUTHORS_FILE.exists():
        appendix_specs.append(("contributors", None, appendix_strings.get("contributors_title", "Contribuïdors")))
    if CHANGELOG_FILE.exists():
        appendix_specs.append(("changelog", CHANGELOG_FILE, changelog_strings.get("title", "Registre de canvis")))

    appendix_pages: list[Page] = [
        Page(href=f"/annex{i}", title=title, source=source, kind=kind)
        for i, (kind, source, title) in enumerate(appendix_specs, start=1)
    ]

    # Colophon: annex-level row after all appendix items
    colophon_strings = strings.get("colophon", {})
    colophon_page = Page(href="/colophon", title=colophon_strings.get("title", "Colofó"), source=None)

    all_pages = front_pages + chapter_pages + appendix_pages + [colophon_page]

    def neighbours(idx: int) -> tuple[Page | None, Page | None]:
        prev_p = all_pages[idx - 1] if idx > 0 else None
        next_p = all_pages[idx + 1] if idx + 1 < len(all_pages) else None
        return prev_p, next_p

    repo_url = config["document"]["repo"].rstrip("/")
    pdf_url = f"{repo_url}/releases/latest/download/nextcat.{lang}.pdf"
    common_ctx = {
        "lang": lang,
        "site_title": doc["title"],
        "repo_url": repo_url,
        "pdf_url": pdf_url,
        "assets": "",
        "css_version": css_version,
    }

    # Index
    index_html = env.get_template("index.html").render(
        **common_ctx,
        page_title=doc["title"],
        title=doc["title"],
        subtitle=doc["subtitle"],
        author=config["document"]["author"],
        version=version,
        version_label=title_page.get("version_label", "Versió"),
        cover_date=cover_date(lang),
        toc_title=toc_strings["title"],
        appendix_title=appendix_strings.get("title", "Annex"),
        front_matter=[{"href": p.href, "title": p.title} for p in front_pages],
        chapters=[{"href": p.href, "title": p.title} for p in chapter_pages],
        appendix=[{"href": p.href, "title": p.title} for p in appendix_pages],
        colophon={"href": colophon_page.href, "title": colophon_page.title},
    )
    (PUBLIC_DIR / "index.html").write_text(index_html)
    console.print(f"  [dim]→[/dim] /")

    # Chapter pages — each one goes into /{slug}/index.html so URLs stay extension-less
    chapter_template = env.get_template("chapter.html")
    for idx, page in enumerate(all_pages):
        prev_p, next_p = neighbours(idx)
        kind = page.kind
        if kind == "changelog":
            intro = changelog_strings.get("intro", "")
            body = _render_markdown(CHANGELOG_FILE.read_text())
            body_html = (f'<p class="lede">{intro}</p>\n' if intro else "") + body
        elif kind == "contributing":
            raw = appendix_strings["contributing_text"].format(repo=repo_url)
            body_html = _render_markdown(raw, strip_leading_h1=False)
        elif kind == "contributors":
            body_html = _contributors_body()
        elif page is colophon_page:
            body_html = _render_colophon(
                config, version, strings, last_modified_date(chapter_files + front_matter_files + [CONFIG_FILE])
            )
        elif page.source is not None and page.source.suffix == ".md":
            body_html = _render_markdown(page.source.read_text())
        else:
            body_html = ""

        html = chapter_template.render(
            **common_ctx,
            page_title=f"{page.title} — {doc['title']}",
            title=page.title,
            chapter_number=page.number,
            chapter_label=chapter_label,
            body_html=body_html,
            body_class="chapter-body" if page.number else "front-body",
            prev={"href": prev_p.href, "title": prev_p.title} if prev_p else None,
            next={"href": next_p.href, "title": next_p.title} if next_p else None,
            toc_title=toc_strings["title"],
        )
        _write_page(page.href.lstrip("/"), html)
        console.print(f"  [dim]→[/dim] {page.href}")

    console.print(f"\n[green bold]Done.[/green bold] Open [cyan]file://{PUBLIC_DIR}/index.html[/cyan]")


def _contributors_body() -> str:
    """Render the contributors list from AUTHORS."""
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


def _render_colophon(config: dict, version: str, strings: dict, modified_text: str) -> str:
    """Render the colophon: muted intro + version, dates, URLs (matches the PDF)."""
    doc = config["document"]
    colophon = strings.get("colophon", {})
    title_page = strings["title_page"]
    version_label = title_page.get("version_label", "Versió")
    modified_label = title_page["modified"]
    generated_label = title_page["generated"]
    text = colophon.get("text", "")
    return (
        f'<div class="colophon">\n'
        f'  <p class="colophon-text">{text}</p>\n'
        f'  <p>{version_label}: {version}</p>\n'
        f'  <p>{modified_label}: {modified_text}<br>\n'
        f'  {generated_label}: {generation_date()}</p>\n'
        f'  <p><a href="{doc["url"]}">{doc["url"]}</a><br>\n'
        f'  <a href="mailto:{doc["email"]}">{doc["email"]}</a></p>\n'
        f'  <p><a href="{doc["repo"]}">{doc["repo"]}</a></p>\n'
        f'  <p class="colophon-license">CC BY-SA 4.0</p>\n'
        f'</div>\n'
    )


if __name__ == "__main__":
    app()
