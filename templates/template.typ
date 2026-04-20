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
  url: "",
  repo: "",
  toc-title: "",
  generated-text: "",
  modified-text: "",
  generated-label: "",
  modified-label: "",
  translation-notice: "",
  body,
) = {
  set document(title: title, author: author)
  set page(paper: "a4", margin: margin-page)
  set text(font: font-body, size: font-size, lang: lang)
  set par(justify: true, leading: 0.65em)

  // Catalan punt volat (geminated l·l / L·L): the Unicode middle dot
  // renders with wide default spacing in most serif fonts. Tighten it
  // when it sits between two L's.
  show regex("[lL]·[lL]"): it => {
    let parts = it.text.split("·")
    box[#parts.at(0)#h(-0.08em)·#h(-0.08em)#parts.at(1)]
  }

  // Link styling
  show link: it => underline(text(fill: color-link, it))

  // Cover
  // Stick short function words (de, a, i, la, el, als...) to the
  // following word so they never orphan at line ends.
  let stick-short(s) = s.replace(
    regex(" (de|a|i|la|el|els|les|al|als|del|dels|per|en) "),
    m => " " + m.captures.at(0) + "\u{00A0}",
  )
  page(numbering: none)[
    #v(3fr)
    #align(center)[
      #block(width: 80%)[
        #set par(justify: false, leading: 0.5em)
        #set text(hyphenate: false)
        #text(size: size-title, weight: "bold")[#stick-short(title)]
        #v(0.4em)
        #text(size: size-subtitle, fill: color-muted)[#stick-short(subtitle)]
      ]
    ]
    #v(4fr)
    #align(right)[
      #text(size: size-h2)[#author] \
      #text(size: font-size, fill: color-light)[#cover-date]
      #v(0.5em)
      #text(size: size-meta, fill: color-faint)[#version]
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
        #version-label: #version

        #v(1.5em)
        #modified-text \
        #generated-text

        #v(1.5em)
        #set text(hyphenate: false)
        #link(url)[#url] \
        #link("mailto:" + email)[#email]

        #v(0.5em)
        #link(repo)[#repo]

        #if translation-notice != "" {
          v(1.5em)
          text(size: size-colophon, fill: color-muted)[#translation-notice]
        }

        #v(1.5em)
        #text(size: size-meta, fill: color-faint)[CC BY-SA 4.0]
      ]
    ]
    #v(1fr)
  ]

  // TOC spacing between main sections
  show outline.entry.where(level: 1): it => {
    v(0.4em)
    it
  }

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

  // Blockquote styling
  show quote: it => {
    block(
      inset: (left: 1em, y: 0.5em),
      stroke: (left: 2pt + color-faint),
    )[#text(fill: color-muted)[#it.body]]
  }

  // Table styling
  set table(stroke: 0.5pt + color-faint)
  show table.cell.where(y: 0): set text(weight: "bold")

  // Horizontal rule styling
  set line(stroke: 0.5pt + color-faint)

  // List styling
  set list(indent: 1em, body-indent: 0.5em)
  set enum(indent: 1em, body-indent: 0.5em)

  body

  // Blank last page
  page(numbering: none, footer: none)[]
}
