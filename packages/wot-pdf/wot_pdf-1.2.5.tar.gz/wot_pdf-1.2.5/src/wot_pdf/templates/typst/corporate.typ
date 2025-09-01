// 🎯 WOT-PDF Corporate Template
// Executive business reports with professional styling

#set document(title: "{title}", author: "{author}")
#set page(
  paper: "a4",
  margin: (left: 2.5cm, right: 2.5cm, top: 3cm, bottom: 3cm),
  numbering: "1",
  number-align: center,
  header: [
    #set text(size: 9pt, fill: rgb("#1f4e79"))
    #grid(
      columns: (1fr, 1fr),
      align: (left, right),
      [*{title}*], 
      [Corporate Report]
    )
    #line(length: 100%, stroke: 1pt + rgb("#1f4e79"))
  ],
  footer: [
    #set text(size: 9pt, fill: rgb("#666666"))
    #line(length: 100%, stroke: 0.5pt + rgb("#cccccc"))
    #v(0.3em)
    #grid(
      columns: (1fr, 1fr, 1fr),
      align: (left, center, right),
      [Confidential], 
      context [Page #counter(page).display()],
      [{date}]
    )
  ]
)

#set text(
  font: ("Times New Roman", "Georgia"),
  size: 11pt,
  lang: "en",
  fill: rgb("#2c2c2c")
)

#set heading(
  numbering: "I.A.1"
)

#show heading.where(level: 1): it => [
  #pagebreak(weak: true)
  #v(1em)
  #block(
    fill: gradient.linear(rgb("#1f4e79"), rgb("#2d5aa0")),
    width: 100%,
    inset: 1.2em,
    radius: 5pt,
    text(fill: white, weight: "bold", size: 20pt)[
      #context counter(heading).display() #it.body
    ]
  )
  #v(1em)
]

#show heading.where(level: 2): it => [
  #v(1.5em)
  #block(
    fill: rgb("#f8f9fa"),
    stroke: (left: 4pt + rgb("#1f4e79")),
    width: 100%,
    inset: (left: 1em, top: 0.7em, bottom: 0.7em),
    text(fill: rgb("#1f4e79"), weight: "bold", size: 16pt)[
      #context counter(heading).display() #it.body
    ]
  )
  #v(0.8em)
]

#show heading.where(level: 3): it => [
  #v(1em)
  #text(fill: rgb("#1f4e79"), weight: "bold", size: 13pt)[
    #context counter(heading).display() #it.body
  ]
  #line(length: 40%, stroke: 1pt + rgb("#1f4e79"))
  #v(0.5em)
]

// Executive summary callout
#let executive-summary(content) = [
  #block(
    fill: rgb("#e8f4fd"),
    stroke: 2pt + rgb("#1f4e79"),
    width: 100%,
    inset: 1.5em,
    radius: 5pt,
    [
      #text(weight: "bold", size: 14pt, fill: rgb("#1f4e79"))[Executive Summary]
      #v(0.5em)
      #content
    ]
  )
]

// Financial tables styling
#show table: it => [
  #v(0.8em)
  #block(
    stroke: (
      top: 2pt + rgb("#1f4e79"),
      bottom: 1pt + rgb("#cccccc"),
      left: none,
      right: none
    ),
    width: 100%,
    above: 0.5em,
    below: 0.5em,
    it
  )
  #v(0.5em)
]

// Lists with corporate styling
#set list(
  indent: 1.2em, 
  marker: text(fill: rgb("#1f4e79"))[▶]
)
#set enum(indent: 1.2em)

// Code blocks (for financial data)
#show raw.where(block: true): it => [
  #block(
    fill: rgb("#f8f9fa"),
    stroke: 1pt + rgb("#dee2e6"),
    width: 100%,
    inset: 1em,
    radius: 3pt,
    text(font: ("SF Mono", "Consolas", "Monaco"), size: 10pt)[#it]
  )
]

// Corporate title page
#align(center)[
  #v(2cm)
  #block(
    fill: gradient.linear(rgb("#1f4e79"), rgb("#2d5aa0")),
    width: 100%,
    inset: 2em,
    radius: 10pt,
    text(fill: white)[
      #text(size: 28pt, weight: "bold")[
        {title}
      ]
      #v(0.5cm)
      #text(size: 16pt)[
        Corporate Business Report
      ]
    ]
  )
  
  #v(2cm)
  #text(size: 14pt, fill: rgb("#1f4e79"))[
    *Prepared by:* {author} \
    *Date:* {date} \
    *Document Type:* Executive Report
  ]
  
  #v(1fr)
  #block(
    fill: rgb("#f8f9fa"),
    stroke: 1pt + rgb("#dee2e6"),
    width: 80%,
    inset: 1em,
    radius: 5pt,
    text(size: 10pt, fill: rgb("#666666"))[
      This document contains confidential and proprietary information. \
      Distribution is restricted to authorized personnel only.
    ]
  )
]

#pagebreak()

// Executive table of contents
#text(size: 18pt, weight: "bold", fill: rgb("#1f4e79"))[
  Table of Contents
]
#v(0.5em)
#line(length: 100%, stroke: 2pt + rgb("#1f4e79"))
#v(1em)

#outline(
  title: none,
  depth: 3
)

#pagebreak()
