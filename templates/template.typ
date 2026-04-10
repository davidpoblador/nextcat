// ABOUTME: Typst document template with a LaTeX-inspired style.
// ABOUTME: Defines page layout, fonts, heading styles, and title page.

#let project(
  title: "",
  subtitle: "",
  author: "",
  email: "",
  lang: "ca",
  version: "",
  repo: "",
  toc-title: "",
  footer-text: "",
  colophon-title: "",
  colophon-text: "",
  body,
) = {
  set document(title: title, author: author)

  set page(
    paper: "a4",
    margin: (top: 3cm, bottom: 3cm, left: 3.5cm, right: 3.5cm),
  )

  set text(
    font: "New Computer Modern",
    size: 11pt,
    lang: lang,
  )

  set par(
    justify: true,
    leading: 0.65em,
  )

  // Cover
  page(numbering: none)[
    #v(3fr)
    #align(center)[
      #text(size: 28pt, weight: "bold")[#title]
      #v(1em)
      #text(size: 16pt, fill: rgb("#555"))[#subtitle]
      #v(3em)
      #text(size: 14pt)[#author]
      #v(0.5em)
      #text(size: 11pt, fill: rgb("#555"))[#email]
      #v(1.5em)
      #text(size: 10pt, fill: rgb("#777"))[v#version]
    ]
    #v(4fr)
    #align(center)[
      #text(size: 8pt, fill: rgb("#999"))[#footer-text]
      #v(0.3em)
      #text(size: 8pt, fill: rgb("#999"))[#repo]
    ]
  ]

  // Page numbering starts after cover
  set page(
    numbering: "1",
    number-align: center,
    footer: context {
      let num = counter(page).display("1")
      align(center, text(size: 9pt, fill: rgb("#777"))[
        #title · v#version
        #h(1fr)
        #num
        #h(1fr)
        #author
      ])
    },
  )
  counter(page).update(1)

  // Heading styles
  set heading(numbering: "1.1.")

  show heading.where(level: 1): it => {
    pagebreak(weak: true)
    v(2em)
    text(size: 20pt, weight: "bold")[#it]
    v(1em)
  }

  show heading.where(level: 2): it => {
    v(1.5em)
    text(size: 14pt, weight: "bold")[#it]
    v(0.75em)
  }

  show heading.where(level: 3): it => {
    v(1em)
    text(size: 12pt, weight: "bold")[#it]
    v(0.5em)
  }

  // List styling
  set list(indent: 1em, body-indent: 0.5em)
  set enum(indent: 1em, body-indent: 0.5em)

  body

  // Colophon
  page(numbering: none, footer: none)[
    #v(1fr)
    #align(center)[
      #text(size: 14pt, weight: "bold")[#colophon-title]
      #v(2em)
      #text(size: 10pt, fill: rgb("#555"))[#colophon-text]
      #v(1.5em)
      #text(size: 10pt, fill: rgb("#555"))[v#version · #footer-text]
      #v(1.5em)
      #text(size: 10pt, fill: rgb("#555"))[#repo]
      #v(3em)
      #text(size: 9pt, fill: rgb("#777"))[CC BY-SA 4.0]
    ]
    #v(1fr)
  ]
}
