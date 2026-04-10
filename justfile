# ABOUTME: Task runner for the Xarter document pipeline.
# ABOUTME: Builds PDFs for all languages and the website from Markdown sources.

default: pdf

# Build PDFs for all languages
pdf:
    uv run python scripts/build.py

# Build the website
site: pdf
    uv run mkdocs build

# Serve the website locally
serve: pdf
    uv run mkdocs serve

# Remove all generated files
clean:
    rm -rf build/ site/ xarter/index.md xarter/changelog.md mkdocs.yml
