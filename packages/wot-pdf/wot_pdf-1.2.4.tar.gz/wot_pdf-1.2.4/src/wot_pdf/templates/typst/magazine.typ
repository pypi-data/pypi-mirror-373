// 📰 WOT-PDF Magazine Style Template  
// Publication-style layout with magazine-like design

#set document(title: "{title}", author: "{author}")
#set page(
  paper: "a4",
  margin: (left: 1.8cm, right: 1.8cm, top: 2cm, bottom: 2cm),
  numbering: "1",
  number-align: center,
  header: [
    #set text(size: 8pt, fill: rgb("#d32f2f"), weight: "bold")
    #grid(
      columns: (1fr, auto, 1fr),
      align: (left, center, right),
      [*{title}*], 
      [●], 
      context [PAGE #counter(page).display()]
    )
    #line(length: 100%, stroke: 0.5pt + rgb("#e0e0e0"))
  ],
  footer: [
    #set text(size: 8pt, fill: rgb("#757575"))
    #line(length: 100%, stroke: 0.5pt + rgb("#e0e0e0"))
    #v(0.3em)
    #align(center)[
      {date} • *WOT-PDF Magazine Engine*
    ]
  ]
)

#set text(
  font: ("Georgia", "Times", "serif"),
  size: 11pt,
  lang: "en",
  fill: rgb("#212121")
)

#set heading(
  numbering: none
)

// Magazine-style headings
#show heading.where(level: 1): it => [
  #pagebreak(weak: true)
  #v(1em)
  #rect(
    fill: rgb("#d32f2f"),
    width: 100%,
    inset: 1.5em,
    radius: 0pt,
    text(fill: white, weight: "bold", size: 22pt)[
      📰 #it.body
    ]
  )
  #v(0.8em)
]

#show heading.where(level: 2): it => [
  #v(1.2em)
  #text(fill: rgb("#1976d2"), weight: "bold", size: 16pt)[
    #it.body
  ]
  #line(length: 60%, stroke: 2pt + rgb("#ff6f00"))
  #v(0.6em)
]

#show heading.where(level: 3): it => [
  #v(1em)
  #text(fill: rgb("#ff6f00"), weight: "bold", size: 14pt)[
    ▶ #it.body
  ]
  #v(0.4em)
]

// Magazine-style code blocks
#show raw.where(block: true): it => [
  #rect(
    fill: rgb("#fafafa"),
    stroke: 1pt + rgb("#e0e0e0"),
    width: 100%,
    inset: 1em,
    radius: 4pt,
    text(font: ("Courier New", "monospace"), fill: rgb("#212121"), size: 10pt)[#it]
  )
]

#show raw.where(block: false): it => [
  #box(
    fill: rgb("#fafafa"),
    inset: (x: 0.3em, y: 0.1em),
    radius: 2pt,
    text(font: ("Courier New", "monospace"), fill: rgb("#d32f2f"), weight: "bold", size: 0.9em)[#it]
  )
]

// Magazine-style lists
#set list(
  indent: 1em, 
  marker: text(fill: rgb("#d32f2f"), size: 12pt)[▸]
)
#set enum(indent: 1em)

// Magazine-style tables
#show table: it => [
  #v(1em)
  #rect(
    stroke: 1pt + rgb("#e0e0e0"),
    fill: rgb("#fafafa"),
    width: 100%,
    inset: 0.8em,
    radius: 4pt,
    it
  )
  #v(0.8em)
]

// Magazine-style quotes (pull quotes)
#show quote: it => [
  #v(1em)
  #rect(
    fill: rgb("#fff3e0"),
    stroke: (left: 4pt + rgb("#ff6f00")),
    width: 100%,
    inset: 1.5em,
    radius: (right: 8pt),
    [
      #text(fill: rgb("#e65100"), size: 13pt, weight: "bold", style: "italic")[
        " #it.body "
      ]
    ]
  )
  #v(1em)
]

// Magazine-style emphasis
#show strong: it => text(fill: rgb("#d32f2f"), weight: "bold")[#it]
#show emph: it => text(fill: rgb("#1976d2"), style: "italic")[#it]

// Magazine-style title page
#align(center)[
  #v(1.5cm)
  #rect(
    fill: gradient.linear(rgb("#d32f2f"), rgb("#1976d2")),
    width: 100%,
    inset: 2em,
    radius: 0pt,
    text(fill: white)[
      #text(size: 28pt, weight: "bold")[
        📰 {title}
      ]
      #v(0.8cm)
      #text(size: 16pt, weight: "regular")[
        Magazine Style Publication
      ]
    ]
  )
  
  #v(1.5cm)
  #text(size: 14pt, fill: rgb("#212121"))[
    *Published by:* {author} \
    *Publication Date:* {date} \
    *Style:* Professional Magazine Layout
  ]
  
  #v(1fr)
  #text(size: 9pt, style: "italic", fill: rgb("#757575"))[
    Premium magazine design powered by WOT-PDF
  ]
]

#pagebreak()

// Magazine table of contents
#text(size: 20pt, weight: "bold", fill: rgb("#d32f2f"))[
  📑 In This Issue
]
#v(0.5em)
#rect(
  fill: gradient.linear(rgb("#d32f2f"), rgb("#ff6f00")),
  width: 100%,
  height: 3pt,
  radius: 0pt
)
#v(1em)

#outline(
  title: none,
  depth: 3
)

#pagebreak()
