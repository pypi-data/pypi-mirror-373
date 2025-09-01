// 📖 WOT-PDF Technical Handbook Template  
// Comprehensive technical manuals and guides

#set document(title: "{title}", author: "{author}")
#set page(
  paper: "a4",
  margin: (left: 2.5cm, right: 2cm, top: 2.5cm, bottom: 2cm),
  numbering: "1",
  number-align: center,
  header: [
    #set text(size: 9pt, fill: rgb("#2e7d32"))
    #grid(
      columns: (1fr, 1fr),
      align: (left, right),
      [*{title}*], 
      [Technical Handbook]
    )
    #line(length: 100%, stroke: 2pt + rgb("#2e7d32"))
  ],
  footer: [
    #set text(size: 9pt, fill: rgb("#424242"))
    #line(length: 100%, stroke: 1pt + rgb("#795548"))
    #v(0.3em)
    #grid(
      columns: (1fr, 1fr),
      align: (left, right),
      [Technical Manual], 
      context [Page #counter(page).display()]
    )
  ]
)

#set text(
  font: ("Arial", "Helvetica", "DejaVu Sans"),
  size: 11pt,
  lang: "en",
  fill: rgb("#424242")
)

#set heading(
  numbering: "1."
)

// Handbook headings with professional styling
#show heading.where(level: 1): it => [
  #pagebreak(weak: true)
  #v(1.5em)
  #rect(
    fill: rgb("#2e7d32"),
    width: 100%,
    inset: 1.5em,
    radius: 8pt,
    text(fill: white, weight: "bold", size: 18pt)[
      📖 #counter(heading).display() #it.body
    ]
  )
  #v(1em)
]

#show heading.where(level: 2): it => [
  #v(1.2em)
  #block(
    fill: rgb("#e8f5e8"),
    stroke: (left: 4pt + rgb("#2e7d32")),
    width: 100%,
    inset: (left: 1.5em, top: 0.8em, bottom: 0.8em),
    radius: (right: 6pt),
    text(fill: rgb("#424242"), weight: "bold", size: 14pt)[
      #counter(heading).display() #it.body
    ]
  )
  #v(0.8em)
]

#show heading.where(level: 3): it => [
  #v(1em)
  #text(fill: rgb("#795548"), weight: "bold", size: 12pt)[
    📋 #counter(heading).display() #it.body
  ]
  #line(length: 40%, stroke: 2pt + rgb("#795548"))
  #v(0.5em)
]

// Professional code blocks
#show raw.where(block: true): it => [
  #block(
    fill: rgb("#424242"),
    stroke: 2pt + rgb("#2e7d32"),
    width: 100%,
    inset: 1.2em,
    radius: 6pt,
    text(font: ("Fira Code", "Consolas", "Monaco"), fill: rgb("#f8f9fa"), size: 10pt)[#it]
  )
]

#show raw.where(block: false): it => [
  #box(
    fill: rgb("#e8f5e8"),
    inset: (x: 0.4em, y: 0.2em),
    radius: 3pt,
    text(font: ("Fira Code", "Consolas", "Monaco"), fill: rgb("#2e7d32"), weight: "bold", size: 0.9em)[#it]
  )
]

// Professional lists
#set list(
  indent: 1.2em, 
  marker: text(fill: rgb("#2e7d32"), size: 12pt)[▪]
)
#set enum(indent: 1.2em)

// Professional tables
#show table: it => [
  #v(1em)
  #block(
    stroke: (
      top: 2pt + rgb("#2e7d32"),
      bottom: 1pt + rgb("#795548"),
      left: none,
      right: none
    ),
    width: 100%,
    inset: 0.8em,
    it
  )
  #v(0.8em)
]

// Professional quotes for important information
#show quote: it => [
  #v(1em)
  #rect(
    fill: rgb("#f8f9fa"),
    stroke: (left: 4pt + rgb("#ff8f00")),
    width: 100%,
    inset: 1.2em,
    radius: (right: 6pt),
    [
      #text(fill: rgb("#795548"), size: 11pt, style: "italic")[
        💡 #it.body
      ]
    ]
  )
  #v(1em)
]

// Professional emphasis
#show strong: it => text(fill: rgb("#2e7d32"), weight: "bold")[#it]
#show emph: it => text(fill: rgb("#795548"), style: "italic")[#it]

// Professional title page
#align(center)[
  #v(2cm)
  #rect(
    fill: rgb("#2e7d32"),
    width: 100%,
    inset: 2.5em,
    radius: 12pt,
    text(fill: white)[
      #text(size: 24pt, weight: "bold")[
        📖 {title}
      ]
      #v(1cm)
      #text(size: 14pt, weight: "regular")[
        Technical Handbook & Manual
      ]
    ]
  )
  
  #v(2cm)
  #text(size: 12pt, fill: rgb("#424242"))[
    *Author:* {author} \
    *Date:* {date} \
    *Document Type:* Technical Manual
  ]
  
  #v(1fr)
  #text(size: 9pt, style: "italic", fill: rgb("#795548"))[
    Professional handbook powered by WOT-PDF
  ]
]

#pagebreak()

// Professional table of contents
#text(size: 18pt, weight: "bold", fill: rgb("#2e7d32"))[
  📋 Contents
]
#v(0.5em)
#rect(
  fill: rgb("#2e7d32"),
  width: 100%,
  height: 3pt,
  radius: 1.5pt
)
#v(1em)

#outline(
  title: none,
  depth: 3
)

#pagebreak()