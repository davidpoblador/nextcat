# Xarter

Foundational document for a Catalan software agency, built from Markdown sources into PDF (via Typst) and a website (via MkDocs).

## Architecture

- `xarter/` -- Canonical Catalan content: markdown chapters, config.toml, strings.toml, license.md
- `translations/<lang>/` -- Translated content (future): strings.toml, chapter .md files, license.md
- `templates/template.typ` -- Typst template with design tokens (LaTeX-style)
- `templates/mkdocs.yml` -- MkDocs template (nav is generated)
- `scripts/build.py` -- Reads config + chapters, generates document.typ, index.md, and mkdocs.yml
- `AUTHORS` -- Author list in `Name <url>` format
- `VERSION` -- Managed by release-please
- `CHANGELOG.md` -- Managed by release-please

## Build pipeline

`just pdf` runs `scripts/build.py` (generates `build/document.typ`) then `typst compile`. The intermediate `.typ` file is deleted after compilation. Output: `build/xarter-{version}.{lang}.pdf`.

`just site` builds the MkDocs website. The build script generates `mkdocs.yml` (from template + nav) and `xarter/index.md` (from chapters + strings).

Both `mkdocs.yml` and `xarter/index.md` are generated artifacts (gitignored).

## Key conventions

- Files prefixed `00-` are front matter (unnumbered, not in TOC)
- Chapters are numbered by filename prefix (`01-`, `02-`, etc.)
- `license.md` in content dir is the localized license for the PDF annex
- All translatable UI strings live in `strings.toml`, not in code or templates
- Non-translatable metadata (author, email, repo) lives in `config.toml`
- Design values (colors, sizes, margins) are tokens at the top of `template.typ`
- TOML values are escaped before interpolation into Typst (security)

## Version strings

Uses dunamai for git-aware versions: `0.1.3` on a tagged commit, `0.1.3.post2.dev0+abc1234` between tags. Falls back to `VERSION` file if no git tags exist.

## Dependencies

All in `[dependency-groups] dev` in pyproject.toml. `uv sync` installs them.

## CI/CD

- `.github/workflows/release.yml` -- release-please + PDF build + attach to GitHub releases
- `.github/workflows/pages.yml` -- build PDF + MkDocs site, deploy to GitHub Pages
- Conventional commits drive versioning: `feat:` bumps minor, `fix:` bumps patch

## Adding a chapter

1. Create `xarter/NN-slug.md` with a `# Title` heading
2. Run `just pdf` -- it appears automatically in TOC, nav, and index

## Translation (future)

Create `translations/<lang>/` with `strings.toml` (translated strings including a `[translation] notice` field), chapter .md files, and `license.md`. The build script will need a `--lang` flag to select the content directory.
