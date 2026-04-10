# ABOUTME: Task runner for the Xarter document pipeline.
# ABOUTME: Builds PDFs for all languages and the website from Markdown sources.

default: pdf

# Build PDFs for all languages
pdf:
    uv run python -m scripts.build

# Build PDF for a single language (e.g. just lang ca)
lang LANG:
    uv run python -m scripts.build {{LANG}}

# Build the website
site: pdf
    uv run mkdocs build

# Serve the website locally
serve: pdf
    uv run mkdocs serve

# Remove all generated files
clean:
    rm -rf build/ site/ book/index.md book/changelog.md book/contributing.md mkdocs.yml
