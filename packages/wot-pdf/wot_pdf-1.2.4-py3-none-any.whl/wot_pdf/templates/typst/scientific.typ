// 🔬 WOT-PDF Scientific Research Template  
// Advanced scientific documentation with formulas

#set document(title: "{title}", author: "{author}")
#set page(
  paper: "a4",
  margin: (left: 2.5cm, right: 2.5cm, top: 2.5cm, bottom: 2.5cm),
  numbering: "1",
  number-align: center,
  header: [
    #set text(size: 9pt, fill: rgb("#1565c0"))
    #grid(
      columns: (1fr, 1fr),
      align: (left, right),
      [*{title}*], 
      [Scientific Research]
    )
    #line(length: 100%, stroke: 2pt + rgb("#1565c0"))
  ],
  footer: [
    #set text(size: 9pt, fill: rgb("#424242"))
    #line(length: 100%, stroke: 1pt + rgb("#90a4ae"))
    #v(0.3em)
    #grid(
      columns: (1fr, 1fr),
      align: (left, right),
      [Research Publication], 
      context [Page #counter(page).display()]
    )
  ]
)

#set text(
  font: ("Computer Modern", "Latin Modern Roman", "Times"),
  size: 11pt,
  lang: "en",
  fill: rgb("#212121")
)

#set heading(
  numbering: "1."
)

// Scientific headings with numbering
#show heading.where(level: 1): it => [
  #pagebreak(weak: true)
  #v(1.5em)
  #rect(
    fill: rgb("#1565c0"),
    width: 100%,
    inset: 1.5em,
    radius: 6pt,
    text(fill: white, weight: "bold", size: 18pt)[
      🔬 #counter(heading).display() #it.body
    ]
  )
  #v(1em)
]

#show heading.where(level: 2): it => [
  #v(1.2em)
  #block(
    fill: rgb("#e3f2fd"),
    stroke: (left: 4pt + rgb("#1565c0")),
    width: 100%,
    inset: (left: 1.5em, top: 0.8em, bottom: 0.8em),
    radius: (right: 4pt),
    text(fill: rgb("#212121"), weight: "bold", size: 14pt)[
      #counter(heading).display() #it.body
    ]
  )
  #v(0.8em)
]

#show heading.where(level: 3): it => [
  #v(1em)
  #text(fill: rgb("#1976d2"), weight: "bold", size: 12pt)[
    📊 #counter(heading).display() #it.body
  ]
  #line(length: 50%, stroke: 2pt + rgb("#1976d2"))
  #v(0.5em)
]

// Scientific code blocks
#show raw.where(block: true): it => [
  #block(
    fill: rgb("#263238"),
    stroke: 2pt + rgb("#1565c0"),
    width: 100%,
    inset: 1.2em,
    radius: 4pt,
    text(font: ("JetBrains Mono", "Fira Code", "Consolas"), fill: rgb("#eceff1"), size: 10pt)[#it]
  )
]

#show raw.where(block: false): it => [
  #box(
    fill: rgb("#e3f2fd"),
    inset: (x: 0.4em, y: 0.2em),
    radius: 3pt,
    text(font: ("JetBrains Mono", "Fira Code", "Consolas"), fill: rgb("#1565c0"), weight: "bold", size: 0.9em)[#it]
  )
]

// Scientific lists
#set list(
  indent: 1.2em, 
  marker: text(fill: rgb("#1565c0"), size: 12pt)[▸]
)
#set enum(indent: 1.2em)

// Scientific tables with professional styling
#show table: it => [
  #v(1em)
  #block(
    stroke: (
      top: 2pt + rgb("#1565c0"),
      bottom: 1pt + rgb("#90a4ae"),
      left: none,
      right: none
    ),
    width: 100%,
    inset: 0.8em,
    it
  )
  #v(0.8em)
]

// Scientific quotes for hypotheses and key findings
#show quote: it => [
  #v(1em)
  #rect(
    fill: rgb("#fff3e0"),
    stroke: (left: 4pt + rgb("#ff8f00")),
    width: 100%,
    inset: 1.2em,
    radius: (right: 6pt),
    [
      #text(fill: rgb("#e65100"), size: 11pt, weight: "bold", style: "italic")[
        💡 #it.body
      ]
    ]
  )
  #v(1em)
]

// Scientific emphasis
#show strong: it => text(fill: rgb("#1565c0"), weight: "bold")[#it]
#show emph: it => text(fill: rgb("#1976d2"), style: "italic")[#it]

// Scientific title page
#align(center)[
  #v(2cm)
  #rect(
    fill: gradient.linear(rgb("#1565c0"), rgb("#1976d2")),
    width: 100%,
    inset: 2.5em,
    radius: 8pt,
    text(fill: white)[
      #text(size: 24pt, weight: "bold")[
        🔬 {title}
      ]
      #v(1cm)
      #text(size: 14pt, weight: "regular")[
        Scientific Research Publication
      ]
    ]
  )
  
  #v(2cm)
  #text(size: 12pt, fill: rgb("#212121"))[
    *Author:* {author} \
    *Publication Date:* {date} \
    *Document Type:* Scientific Research
  ]
  
  #v(1fr)
  #text(size: 9pt, style: "italic", fill: rgb("#757575"))[
    Advanced research powered by WOT-PDF Scientific Engine
  ]
]

#pagebreak()

// Scientific table of contents
#text(size: 18pt, weight: "bold", fill: rgb("#1565c0"))[
  📋 Table of Contents
]
#v(0.5em)
#rect(
  fill: gradient.linear(rgb("#1565c0"), rgb("#1976d2")),
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
