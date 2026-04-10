# ABOUTME: Task runner for the Xarter document pipeline.
# ABOUTME: Converts markdown chapters to Typst via cmarker, then compiles to PDF.

default: pdf

# Generate the Typst document from markdown chapters
typst:
    uv run python scripts/build.py

# Compile the Typst document to PDF
pdf: typst
    typst compile --root . build/document.typ build/document.pdf

# Watch for changes and recompile (run `just typst` first)
watch: typst
    typst watch --root . build/document.typ build/document.pdf

# Remove generated files
clean:
    rm -rf build/

# List all chapters
chapters:
    @ls -1 xarter/*.md
