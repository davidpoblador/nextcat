# ABOUTME: Task runner for the Xarter document pipeline.
# ABOUTME: Builds PDFs for all languages and the website from Markdown sources.

default: pdf

# Build PDFs for all languages
pdf:
    uv run xarter

# Build PDF for a single language (e.g. just lang ca)
lang LANG:
    uv run xarter {{LANG}}

# Build the website
site: pdf
    uv run --group docs mkdocs build

# Serve the website locally
serve: pdf
    uv run --group docs mkdocs serve

# Remove all generated files
clean:
    rm -rf build/ site/ xarter/index.md xarter/changelog.md xarter/contributing.md mkdocs.yml
