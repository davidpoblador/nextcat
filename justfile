# ABOUTME: Task runner for the Xarter document pipeline.
# ABOUTME: Converts markdown chapters to Typst via cmarker, then compiles to PDF.

version := `uv run python -c "from dunamai import Style, Version; print(Version.from_git().serialize(style=Style.Pep440))" 2>/dev/null || cat VERSION`
lang := `uv run python -c "import tomllib; print(tomllib.load(open('xarter/strings.toml','rb'))['lang'])" 2>/dev/null || echo ca`

default: pdf

# Generate the Typst document from markdown chapters
typst:
    uv run python scripts/build.py

# Compile the Typst document to PDF
pdf: typst
    typst compile --root . build/document.typ build/xarter-{{version}}.{{lang}}.pdf

# Watch for changes and recompile (run `just typst` first)
watch: typst
    typst watch --root . build/document.typ build/xarter-{{version}}.{{lang}}.pdf

# Build the website
site:
    uv run mkdocs build

# Serve the website locally
serve:
    uv run mkdocs serve

# Remove generated files
clean:
    rm -rf build/ site/

# List all chapters
chapters:
    @ls -1 xarter/*.md
