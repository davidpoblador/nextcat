# NextCat

Foundational document for a Catalan digital strategy, rendered from Markdown sources into a PDF (via Typst) and a static HTML reader (via Jinja2 + Python-Markdown).

## Architecture

- `book/` -- Canonical Catalan content: markdown chapters, strings.toml, license.md, about-author.md, CNAME
- `translations/<lang>/` -- Translated content (future): strings.toml, chapter .md files, license.md
- `templates/template.typ` -- Typst template with design tokens (LaTeX-style)
- `templates/site/` -- Jinja2 templates + CSS for the HTML reader
- `scripts/build.py` -- PDF builder entrypoint (`uv run python -m scripts.build`)
- `scripts/site.py` -- HTML reader builder (`uv run python -m scripts.site`)
- `scripts/generate.py` -- Shared helpers (chapter resolution, Typst document assembly, changelog parsing)
- `fonts/` -- Libertinus Serif (SIL OFL, checked into the repo)
- `config.toml` -- Non-translatable metadata (author, email, url, repo)
- `AUTHORS` -- Author list in `Name <url>` format
- `VERSION` -- Managed by release-please
- `EDITION` -- Human-managed integer; bumped by hand for each public reissue (e.g. KDP upload)
- `CHANGELOG.md` -- Managed by release-please

## Build pipeline

`just pdf` runs `uv run python -m scripts.build`, which generates `.typ` files in `build/` then compiles them with the `typst` Python binding (no `typst` CLI needed). Fonts are loaded from `fonts/` via `font_paths`. Each language emits two artifacts: `build/nextcat-{version}.{lang}.pdf` (reader edition, no changelog) and `build/nextcat-{version}.{lang}-full.pdf` (archival edition). Intermediate `.typ` files are deleted after compilation.

`just site` (alias `just book`) runs `uv run python -m scripts.site`, which renders each chapter through Python-Markdown into a Jinja2 template. Output lives under `public/` (gitignored): one HTML page per chapter, plus index/cover, appendix (license, key concepts glossary, about-author, contributing notes, contributors, changelog) and colophon. The stylesheet and Libertinus Serif fonts are copied alongside; `book/CNAME` is copied to `public/CNAME` so GitHub Pages picks up the custom domain.

## Key conventions

- Files prefixed `00-` are front matter (unnumbered; in the HTML reader they're listed as chapter 0)
- Chapters are numbered by filename prefix (`01-`, `02-`, etc.)
- `license.md` in content dir is the localized license for the PDF annex / HTML appendix
- All translatable UI strings live in `strings.toml`, not in code or templates
- Non-translatable metadata (author, email, repo) lives in `config.toml`
- Design values (colors, sizes, margins) are tokens at the top of `template.typ` and in `templates/site/style.css`
- TOML values are escaped before interpolation into Typst (security)

## Version strings

Uses dunamai for git-aware versions: `0.1.3` on a tagged commit, `0.1.3.post2.dev0+abc1234` between tags. Falls back to `VERSION` file if no git tags exist.

## Edition vs version

Two independent identifiers travel through every artifact:

- **Version** (engineering build identifier): the dunamai/`VERSION` string above. Changes on every release-please cut and on every dev rebuild between tags. Surfaced on the metadata page and colophon as `Versió: x.y.z`.
- **Edition** (public-facing reissue counter): an integer in `EDITION`, managed by hand. Bump it with `just bump-edition` before each public reissue (e.g. a new KDP upload). Localised to a phrase like `Edició 1` via the `[edition]` table in `strings.toml` (`phrase = "Edició {n}"`) and surfaced on the cover, metadata page and colophon. The EPUB also writes the integer to OPF metadata as `<meta property="schema:bookEdition">`.

The version reflects "what code built this"; the edition reflects "which public release this is". Translations supply their own phrase template under `[edition]` in `translations/<lang>/strings.toml` (e.g. `"Edición {n}"`, `"Edition {n}"`). Spelled-out ordinals were considered and dropped — see GitHub issue #74 for the rationale and revisit triggers.

## Dependencies

All deps (typer, babel, dunamai, jinja2, markdown, typst) live in `[dependency-groups] dev` in pyproject.toml. `[project] dependencies` is empty. Install with `uv sync`. The `typst` Python package bundles the compiler, so no separate Typst install is required. Libertinus Serif OTFs in `fonts/` are checked into the repo and passed to the compiler via `font_paths`.

## CI/CD

- `.github/workflows/release.yml` -- release-please + PDF build + attach to GitHub releases (stable `nextcat.{lang}.pdf` alias uploaded alongside versioned artifacts)
- `.github/workflows/pages.yml` -- build the static HTML reader and deploy to GitHub Pages (custom domain via `book/CNAME`)
- Conventional commits drive versioning: `feat:` bumps minor, `fix:` bumps patch

## Adding a chapter

1. Create `book/NN-slug.md` with a `# Title` heading
2. Run `just pdf` (and/or `just site`) — it appears automatically in both outputs

## Keeping PDF and HTML reader in sync

Both are generated from the same markdown sources but assemble the annex differently.

- **Chapters** (`book/NN-*.md`): Automatically picked up by both. No extra work needed.
- **Front matter** (`book/00-*.md`): Automatically picked up by both.
- **Annex sections** (license, key concepts glossary, about-author, contributing notes, contributors, changelog): assembled by the two build scripts. The PDF appendix lives in `scripts/generate.py → build_typst()`; the HTML appendix lives in `scripts/site.py → build()`. When adding a new annex section, update both.
- **Colophon**: Generated by all three build scripts (`build_typst` in generate.py for PDF, `_render_colophon` in site.py for HTML, `_colophon_body` in epub.py for EPUB). The intro line is format-specific: `[colophon]` in `strings.toml` defines `text_pdf`, `text_epub`, `text_html` — every translation must supply all three.
- **Excluded files**: `index.md`, `license.md`, `about-author.md`, and `conceptes-clau.md` in `book/` are excluded from the chapter list.

## Translation (future)

Create `translations/<lang>/` with `strings.toml` (translated strings including a `[translation] notice` field), chapter .md files, and `license.md`. The PDF build script already handles translations; the HTML reader currently builds only the canonical language (to be extended).

## Writing the book: tone, language and quality

The book is a public-policy essay, not documentation. Content quality, register and linguistic correctness are the primary deliverable — they are not negotiable, and agents must hold themselves to the same bar as a human author writing under their own name.

### Preserve the existing voice

- Read the surrounding chapters before writing a single sentence. The register is **dignified, essayistic, pragmatic and direct**: confident without being triumphalist, critical without being polemic, evidence-led, opinionated where opinions are earned. Sentences can be long, but never ornamental.
- **Anchor claims in facts**, with linked primary sources in the `[Font: [Title](url)]` pattern already used throughout. No unsourced statistics, no "it is said that". When you cannot verify a fact, leave it out.
- **No marketing tone, no hype, no empty adjectives.** Avoid *revolucionari*, *disruptiu*, *transformador* as standalone praise. If something is transformative, show it.
- **No emojis**, no exclamation marks outside quotations, no rhetorical questions as filler. Match the cadence of adjacent paragraphs.

### Catalan as native, not translated

The book is written in **native-quality Catalan**, not a translation of English or Spanish text. When adding or editing content:

- **Write as a fluent Catalan speaker would write.** Do not translate English or Spanish phrase by phrase. Reorder clauses, replace idioms, pick collocations that sound native. If a paragraph reads like it was written in another language first, rewrite it.
- **Avoid calques and barbarisms.** Common traps to refuse: *jugar un rol* (use *tenir un paper*), *en base a* (*a partir de*, *sobre la base de*), *o sigui* as discourse marker (*és a dir*), *tenir que* (*haver de*), *donar-se compte* (*adonar-se*), *lograr*, *intentar de*, *aprofitar de*. Spanish verbal regimes leak easily — check prepositions.
- **Watch the classic Catalan pain points**: apostrophes (`l'estratègia`, `d'un`, `n'és`), accents (`è`/`é`, `à`/`á`, `ó`/`ò`), the `per`/`per a` distinction, weak pronouns (*pronoms febles*) and their combinations, possessives without article (*la meva* vs *meva*), and relative pronouns (*el qual* vs *que* vs *qui*).
- **Prefer Termcat for technical terminology.** Use *tauler* for *dashboard*, *núvol* for *cloud*, *codi obert* for *open source*. Where no settled Catalan term exists, keep the English term in italics (*dogfooding*, *API*) and explain it the first time. Never invent translations.
- **Source titles stay in the original language.** Citations, link titles and quoted passages are not translated. `[Font: [State of the Digital Decade 2025, Comissió Europea](...)]` is correct; do not localize report titles.

### Triple-check before shipping

Before any edit to `book/**/*.md` is considered done, the text must pass **three independent reads**:

1. **Meaning pass.** Does each sentence say exactly what it intends? Are claims supported? Is the logical flow sound?
2. **Language pass.** Grammar, spelling, accents, apostrophes, pronoms febles, `per`/`per a`, concordances. Read aloud — cadence exposes awkward constructions.
3. **Register pass.** Does it match the voice of the surrounding chapters? No tonal drift, no AI tells (*cal destacar que*, *és important remarcar*, over-structured bullet lists where prose would do), no filler.

If the agent is not fully confident on the Catalan quality of a proposed change, it must say so explicitly in the PR description rather than ship silently. An uncertain edit flagged for review is cheap; a plausible-looking but subtly wrong edit erodes the document's credibility.

### Translations (future)

When translating the book into another language, apply the same bar: native-quality prose in the target language, not a word-for-word mapping of the Catalan. The translation lives in `translations/<lang>/` with its own `strings.toml` and chapter files. Keep the structural parallelism with the canonical Catalan, but allow local idiom and cadence to breathe.

## Contributing

See `CONTRIBUTING.md` for the full guide. Key points for agents:

- Always work on a branch, never push directly to `main`
- Use conventional commits in English (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `ci:`)
- PR titles must also follow conventional commit syntax (they become the squash commit message)
- Run `just clean && just pdf && just site` before opening a PR
- Content changes go in `book/*.md`, never edit generated files (`build/`, `public/`)
- Strings and labels go in `strings.toml`, not hardcoded in templates or scripts
- Do not edit `VERSION`, `CHANGELOG.md`, or `.release-please-manifest.json` manually
- Always include a `Co-Authored-By` trailer when AI tools are used to generate content or code
