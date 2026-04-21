# ABOUTME: Task runner for the NextCat document pipeline.
# ABOUTME: Builds PDFs for all languages and the website from Markdown sources.

default: pdf

# Build PDFs for all languages
pdf:
    uv run python -m scripts.build

# Build PDF for a single language (e.g. just lang ca)
lang LANG:
    uv run python -m scripts.build {{LANG}}

# Build the static HTML reader into public/
site: pdf
    uv run python -m scripts.site

# Build the book (alias for `site`)
book: site

# Remove all generated files
clean:
    rm -rf build/ public/
