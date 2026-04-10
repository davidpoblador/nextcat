// ABOUTME: Typst document template with a LaTeX-inspired style.
// ABOUTME: Defines page layout, fonts, heading styles, and title page.

// Design tokens
#let font-body = "New Computer Modern"
#let font-size = 11pt
#let color-body = rgb("#000")
#let color-muted = rgb("#555")
#let color-light = rgb("#777")
#let color-faint = rgb("#999")
#let color-link = rgb("#2244aa")
#let margin-page = (top: 3cm, bottom: 3cm, left: 3.5cm, right: 3.5cm)
#let size-title = 28pt
#let size-subtitle = 18pt
#let size-h1 = 20pt
#let size-h2 = 14pt
#let size-h3 = 12pt
#let size-colophon = 10pt
#let size-meta = 8pt

#let project(
  title: "",
  subtitle: "",
  author: "",
  email: "",
  lang: "ca",
  version: "",
  version-label: "Versió",
  cover-date: "",
  repo: "",
  toc-title: "",
  generated-text: "",
  modified-text: "",
  generated-label: "",
  modified-label: "",
  colophon-title: "",
  colophon-text: "",
  translation-notice: "",
  body,
) = {
  set document(title: title, author: author)
  set page(paper: "a4", margin: margin-page)
  set text(font: font-body, size: font-size, lang: lang)
  set par(justify: true, leading: 0.65em)

  // Cover
  page(numbering: none)[
    #v(3fr)
    #align(center)[
      #text(size: size-title, weight: "bold")[#title]
      #v(0.5em)
      #text(size: size-subtitle, fill: color-muted)[#subtitle]
    ]
    #v(4fr)
    #align(right)[
      #text(size: size-h2)[#author]
      #v(0.3em)
      #text(size: font-size, fill: color-light)[#cover-date] \
      #text(size: font-size, fill: color-light)[#version-label #version]
    ]
  ]

  // Blank verso of cover
  page(numbering: none)[]

  // Pages count from here but numbers are hidden until after the TOC
  set page(numbering: none)
  counter(page).update(1)

  // Metadata page (verso, facing the prefaci)
  page(numbering: none)[
    #v(1fr)
    #align(right)[
      #block[
        #text(weight: "bold")[#title] \
        #text(fill: color-muted)[#subtitle]

        #v(1.5em)
        #version-label #version

        #v(1.5em)
        #modified-text \
        #generated-text

        #v(1.5em)
        #set text(hyphenate: false)
        #link(repo)[#repo] \
        #link("mailto:" + email)[#email]

        #if translation-notice != "" {
          v(1.5em)
          text(size: size-colophon, fill: color-muted)[#translation-notice]
        }
      ]
    ]
    #v(1fr)
  ]

  // Heading styles
  set heading(numbering: "1.1.")

  show heading.where(level: 1): it => {
    pagebreak(weak: true)
    v(2em)
    text(size: size-h1, weight: "bold")[#it]
    v(1em)
  }

  show heading.where(level: 2): it => {
    v(1.5em)
    text(size: size-h2, weight: "bold")[#it]
    v(0.75em)
  }

  show heading.where(level: 3): it => {
    v(1em)
    text(size: size-h3, weight: "bold")[#it]
    v(0.5em)
  }

  // Link styling
  show link: it => underline(text(fill: color-link, it))

  // List styling
  set list(indent: 1em, body-indent: 0.5em)
  set enum(indent: 1em, body-indent: 0.5em)

  body

  // Colophon
  page(numbering: none, footer: none)[
    #v(1fr)
    #align(center)[
      #text(size: size-h2, weight: "bold")[#colophon-title]
      #v(2em)
      #text(size: size-colophon, fill: color-muted)[#colophon-text]
      #v(1.5em)
      #text(size: size-colophon, fill: color-muted)[v#version]
      #v(0.5em)
      #text(size: size-colophon, fill: color-muted)[#generated-text]
      #v(0.3em)
      #text(size: size-colophon, fill: color-muted)[#modified-text]
      #v(1.5em)
      #text(size: size-colophon, fill: color-muted)[#repo]
      #v(3em)
      #text(size: size-meta, fill: color-light)[CC BY-SA 4.0]
    ]
    #v(1fr)
  ]

  // Blank last page
  page(numbering: none, footer: none)[]
}
