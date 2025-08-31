// 🎯 WOT-PDF Academic Template
// Research papers with citations and mathematical notation

#set document(title: "{title}", author: "{author}")
#set page(
  paper: "a4",
  margin: (left: 3cm, right: 3cm, top: 3cm, bottom: 3cm),
  numbering: "1",
  number-align: center,
  header: [
    #set text(size: 9pt, fill: gray)
    #grid(
      columns: (1fr, 1fr),
      align: (left, right),
      [*{title}*], 
      [Academic Paper]
    )
    #line(length: 100%, stroke: 0.5pt + gray)
  ]
)

#set text(
  font: ("Times New Roman", "Georgia"),
  size: 12pt,
  lang: "en"
)

#set heading(
  numbering: "1."
)

// Academic paper title formatting
#show heading.where(level: 1): it => [
  #v(1.5em)
  #align(center)[
    #text(size: 16pt, weight: "bold")[
      #counter(heading).display() #it.body
    ]
  ]
  #v(1em)
]

#show heading.where(level: 2): it => [
  #v(1.2em)
  #text(weight: "bold", size: 14pt)[
    #counter(heading).display() #it.body
  ]
  #v(0.5em)
]

#show heading.where(level: 3): it => [
  #v(1em)
  #text(weight: "bold", style: "italic", size: 12pt)[
    #counter(heading).display() #it.body
  ]
  #v(0.3em)
]

// Abstract environment
#let abstract(content) = [
  #v(1em)
  #block(
    width: 100%,
    inset: (left: 2em, right: 2em, top: 1em, bottom: 1em),
    stroke: none,
    fill: rgb("#f9f9f9"),
    radius: 3pt,
    [
      #align(center)[
        #text(weight: "bold", size: 11pt)[Abstract]
      ]
      #v(0.5em)
      #text(size: 10pt, style: "italic")[#content]
    ]
  )
  #v(1em)
]

// Keywords environment
#let keywords(words) = [
  #v(0.5em)
  #text(weight: "bold", size: 10pt)[Keywords: ]
  #text(style: "italic", size: 10pt)[#words.join(", ")]
  #v(1em)
]

// Mathematical equations
#set math.equation(numbering: "(1)")
#show math.equation.where(block: true): it => [
  #v(0.8em)
  #align(center)[#it]
  #v(0.8em)
]

// Figures
#let figure-caption(content) = [
  #v(0.5em)
  #align(center)[
    #text(size: 10pt, weight: "bold")[
      Figure #counter(figure).display(): #content
    ]
  ]
  #v(0.8em)
]

// Tables with academic styling
#show table: it => [
  #v(0.8em)
  #align(center)[
    #block(
      stroke: (
        top: 1.5pt + black,
        bottom: 1.5pt + black,
        left: none,
        right: none
      ),
      above: 0.5em,
      below: 0.5em,
      it
    )
  ]
  #v(0.5em)
]

// Citations (simplified)
#let cite(key) = [
  #text(fill: blue)[\[#key\]]
]

// References section
#let references(content) = [
  #pagebreak()
  #text(size: 16pt, weight: "bold")[References]
  #v(1em)
  #text(size: 10pt)[#content]
]

// Code blocks for academic use
#show raw.where(block: true): it => [
  #block(
    fill: rgb("#f8f8f8"),
    stroke: 1pt + rgb("#e0e0e0"),
    width: 100%,
    inset: 1em,
    radius: 2pt,
    text(font: ("Computer Modern Mono", "Consolas", "Monaco"), size: 9pt)[#it]
  )
]

// Lists
#set list(indent: 1em, marker: "•")
#set enum(indent: 1em)

// Academic title page
#align(center)[
  #v(3cm)
  #text(size: 20pt, weight: "bold")[
    {title}
  ]
  
  #v(2cm)
  #text(size: 14pt)[
    {author}
  ]
  
  #v(1cm)
  #text(size: 12pt)[
    Department of Computer Science \
    University Name \
    Location
  ]
  
  #v(2cm)
  #text(size: 12pt)[
    {date}
  ]
  
  #v(1fr)
  #text(size: 10pt, style: "italic")[
    Academic paper generated with WOT-PDF
  ]
]

#pagebreak()

// Table of contents
#outline(
  title: [Table of Contents],
  depth: 3
)

#pagebreak()
