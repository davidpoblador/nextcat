# Style Guide

## Typography and formatting

### Bold and italic

We use **bold** to highlight key concepts and *italic* for technical or foreign terms. They can also be combined as ***bold and italic*** when needed.

### Lists

Unordered lists:

- First-level item
- Another item
  - Nested sub-item
  - Another sub-item
- Third item

Ordered lists:

1. First step
2. Second step
3. Third step

### Code

Inline code: `python build.py` or `just pdf`.

Code blocks with syntax highlighting:

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"
```

```toml
[document]
author = "Xarter S.L."
repo = "https://github.com/davidpoblador/xarter"
```

## Content structure

### Third-level headings

We use up to three levels of headings within each chapter. The first level (`#`) is the chapter title, the second (`##`) is for main sections, and the third (`###`) for subsections.

#### Fourth-level headings

In exceptional cases, a fourth level may be used for very specific subdivisions. Overuse should be avoided to maintain readability.

## Links and references

External links use standard Markdown syntax: [Typst website](https://typst.app/) or [project repository](https://github.com/davidpoblador/xarter).

## Quotes and blocks

> Quotes are used to highlight textual fragments from other sources or to emphasize an important principle of the charter.

## Tables

| Technology | Domain | Maturity |
|---|---|---|
| Python | Backend | High |
| Typst | Documents | Medium |
| MkDocs | Web | High |

## Separators

The horizontal separator is used to divide thematically different sections within the same chapter.

---

This section, for example, is separated from the previous one by a horizontal separator.
