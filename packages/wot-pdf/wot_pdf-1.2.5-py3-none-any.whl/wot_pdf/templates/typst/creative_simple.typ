// 🎨 WOT-PDF Creative Template  
// Modern, artistic design for creative documents

#set document(title: "{title}", author: "{author}")
#set page(
  paper: "a4",
  margin: (left: 2.5cm, right: 2.5cm, top: 3cm, bottom: 3cm),
  numbering: "1",
  number-align: center,
  header: [
    #set text(size: 9pt, fill: rgb("#e74c3c"))
    #grid(
      columns: (1fr, 1fr),
      align: (left, right),
      [*{title}*], 
      [Creative Design]
    )
    #line(length: 100%, stroke: 2pt + rgb("#e74c3c"))
  ],
  footer: [
    #set text(size: 9pt, fill: rgb("#666666"))
    #line(length: 100%, stroke: 1pt + rgb("#f39c12"))
    #v(0.3em)
    #grid(
      columns: (1fr, 1fr),
      align: (left, right),
      [Creative PDF], 
      context [Page #counter(page).display()]
    )
  ]
)

#set text(
  font: ("Inter", "Arial"),
  size: 11pt,
  lang: "en",
  fill: rgb("#2c3e50")
)

#set heading(
  numbering: "1."
)

// Creative headings with vibrant colors
#show heading.where(level: 1): it => [
  #pagebreak(weak: true)
  #v(1.5em)
  #rect(
    fill: gradient.linear(rgb("#e74c3c"), rgb("#f39c12")),
    width: 100%,
    inset: 1.5em,
    radius: 10pt,
    text(fill: white, weight: "bold", size: 20pt)[
      #counter(heading).display() #it.body
    ]
  )
  #v(1em)
]

#show heading.where(level: 2): it => [
  #v(1.2em)
  #block(
    fill: rgb("#ecf0f1"),
    stroke: (left: 5pt + rgb("#3498db")),
    width: 100%,
    inset: (left: 1.5em, top: 1em, bottom: 1em),
    radius: (right: 8pt),
    text(fill: rgb("#2c3e50"), weight: "bold", size: 16pt)[
      #counter(heading).display() #it.body
    ]
  )
  #v(0.8em)
]

#show heading.where(level: 3): it => [
  #v(1em)
  #text(fill: rgb("#f39c12"), weight: "bold", size: 13pt)[
    🎨 #counter(heading).display() #it.body
  ]
  #line(length: 50%, stroke: 2pt + rgb("#f39c12"))
  #v(0.5em)
]

// Artistic code blocks
#show raw.where(block: true): it => [
  #block(
    fill: rgb("#2c3e50"),
    stroke: 3pt + rgb("#e74c3c"),
    width: 100%,
    inset: 1.5em,
    radius: 8pt,
    text(font: ("Fira Code", "Consolas", "Monaco"), fill: rgb("#ecf0f1"), size: 10pt)[#it]
  )
]

#show raw.where(block: false): it => [
  #box(
    fill: rgb("#f39c12"),
    inset: (x: 0.4em, y: 0.2em),
    radius: 4pt,
    text(font: ("Fira Code", "Consolas", "Monaco"), fill: white, weight: "bold", size: 0.9em)[#it]
  )
]

// Creative lists with colorful markers
#set list(
  indent: 1.5em, 
  marker: text(fill: rgb("#e74c3c"), size: 14pt)[●]
)
#set enum(indent: 1.5em)

// Artistic tables
#show table: it => [
  #v(1em)
  #block(
    stroke: none,
    radius: 8pt,
    fill: rgb("#ecf0f1"),
    inset: 0.5em,
    it
  )
  #v(0.8em)
]

// Creative quotes
#show quote: it => [
  #v(1em)
  #rect(
    fill: gradient.linear(rgb("#3498db"), rgb("#9b59b6")),
    width: 100%,
    inset: 1.5em,
    radius: 12pt,
    [
      #text(fill: white, size: 12pt, style: "italic")[
        💭 #it.body
      ]
    ]
  )
  #v(1em)
]

// Creative emphasis
#show strong: it => text(fill: rgb("#e74c3c"), weight: "bold", size: 1.1em)[#it]
#show emph: it => text(fill: rgb("#3498db"), style: "italic")[#it]

// Creative title page
#align(center)[
  #v(2.5cm)
  #rect(
    fill: gradient.linear(rgb("#e74c3c"), rgb("#f39c12"), rgb("#3498db")),
    width: 100%,
    inset: 2.5em,
    radius: 20pt,
    text(fill: white)[
      #text(size: 28pt, weight: "bold")[
        🎨 {title}
      ]
      #v(1cm)
      #text(size: 16pt, weight: "normal")[
        Creative Design Document
      ]
    ]
  )
  
  #v(2cm)
  #text(size: 14pt, fill: rgb("#2c3e50"))[
    *Created by:* {author} \
    *Date:* {date} \
    *Style:* Modern Creative Design
  ]
  
  #v(1fr)
  #text(size: 10pt, style: "italic", fill: rgb("#666666"))[
    Artistic design powered by WOT-PDF Creative Engine
  ]
]

#pagebreak()

// Creative table of contents
#text(size: 20pt, weight: "bold", fill: rgb("#e74c3c"))[
  🎯 Contents
]
#v(0.5em)
#rect(
  fill: gradient.linear(rgb("#e74c3c"), rgb("#f39c12")),
  width: 100%,
  height: 4pt,
  radius: 2pt
)
#v(1em)

#outline(
  title: none,
  depth: 3
)

#pagebreak()
