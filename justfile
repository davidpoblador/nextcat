# ABOUTME: Task runner for the NextCat document pipeline.
# ABOUTME: Builds PDFs, EPUBs and the website from Markdown sources.

default: all

# Build every artifact (PDFs, EPUBs, HTML reader)
all: pdf epub site

# Build PDFs for all languages (reader + full variants)
pdf:
    uv run python -m scripts.build

# Build PDF for a single language (e.g. just lang ca)
lang LANG:
    uv run python -m scripts.build {{LANG}}

# Build EPUBs (reader + full variants)
epub:
    uv run python -m scripts.epub

# Build the static HTML reader into public/
site: pdf
    uv run python -m scripts.site

# Build the book (alias for `site`)
book: site

# Serve the built site locally (default port 8765, IPv4 only)
serve PORT="8765": site
    cd public && uv run python -m http.server --bind 127.0.0.1 {{PORT}}

# Increment the human-managed edition number in EDITION
bump-edition:
    uv run python -c "from pathlib import Path; p = Path('EDITION'); p.write_text(f'{int(p.read_text().strip()) + 1}\n')"

# Remove all generated files
clean:
    rm -rf build/ public/
