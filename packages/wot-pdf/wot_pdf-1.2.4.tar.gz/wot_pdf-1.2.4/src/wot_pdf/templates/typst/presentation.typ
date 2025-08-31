// 🎯 WOT-PDF Presentation Template  
// Slide-like layout for presentations in PDF format

#set document(title: "{title}", author: "{author}")
#set page(
  paper: "a4",
  margin: (left: 2cm, right: 2cm, top: 2cm, bottom: 2cm),
  numbering: "1",
  number-align: center,
  header: [
    #set text(size: 10pt, fill: rgb("#1976d2"), weight: "bold")
    #grid(
      columns: (1fr, 1fr),
      align: (left, right),
      [*{title}*], 
      [Presentation]
    )
    #line(length: 100%, stroke: 2pt + rgb("#1976d2"))
  ],
  footer: [
    #set text(size: 9pt, fill: rgb("#424242"))
    #line(length: 100%, stroke: 1pt + rgb("#90caf9"))
    #v(0.3em)
    #context [
      #align(center)[Slide #counter(page).display()]
    ]
  ]
)

#set text(
  font: ("Arial", "Helvetica", "DejaVu Sans"),
  size: 12pt,
  lang: "en",
  fill: rgb("#212121")
)

#set heading(
  numbering: none
)

// Presentation-style headings (slide titles)
#show heading.where(level: 1): it => [
  #pagebreak(weak: true)
  #v(1em)
  #rect(
    fill: gradient.linear(rgb("#1976d2"), rgb("#42a5f5")),
    width: 100%,
    inset: 2em,
    radius: 8pt,
    text(fill: white, weight: "bold", size: 22pt)[
      🎯 #it.body
    ]
  )
  #v(1.5em)
]

#show heading.where(level: 2): it => [
  #v(1.2em)
  #text(fill: rgb("#1976d2"), weight: "bold", size: 16pt)[
    ▶ #it.body
  ]
  #line(length: 70%, stroke: 2pt + rgb("#42a5f5"))
  #v(0.8em)
]

#show heading.where(level: 3): it => [
  #v(1em)
  #text(fill: rgb("#1e88e5"), weight: "bold", size: 14pt)[
    ● #it.body
  ]
  #v(0.6em)
]

// Presentation code blocks
#show raw.where(block: true): it => [
  #block(
    fill: rgb("#263238"),
    stroke: 2pt + rgb("#1976d2"),
    width: 100%,
    inset: 1.5em,
    radius: 8pt,
    text(font: ("Consolas", "Monaco", "Courier New"), fill: rgb("#eceff1"), size: 11pt)[#it]
  )
]

#show raw.where(block: false): it => [
  #box(
    fill: rgb("#e3f2fd"),
    inset: (x: 0.5em, y: 0.3em),
    radius: 4pt,
    text(font: ("Consolas", "Monaco", "Courier New"), fill: rgb("#1976d2"), weight: "bold", size: 1em)[#it]
  )
]

// Presentation bullet points - large and clear
#set list(
  indent: 1.5em, 
  marker: text(fill: rgb("#1976d2"), size: 16pt)[●]
)
#set enum(indent: 1.5em)

// Presentation tables - clean and readable
#show table: it => [
  #v(1.5em)
  #rect(
    stroke: 2pt + rgb("#1976d2"),
    fill: rgb("#f5f5f5"),
    width: 100%,
    inset: 1em,
    radius: 6pt,
    it
  )
  #v(1.2em)
]

// Presentation quotes for key points
#show quote: it => [
  #v(1.5em)
  #rect(
    fill: gradient.linear(rgb("#e3f2fd"), rgb("#bbdefb")),
    stroke: (left: 6pt + rgb("#1976d2")),
    width: 100%,
    inset: 2em,
    radius: (right: 10pt),
    [
      #text(fill: rgb("#0d47a1"), size: 14pt, weight: "bold", style: "italic")[
        💬 #it.body
      ]
    ]
  )
  #v(1.5em)
]

// Presentation emphasis - bold and visible
#show strong: it => text(fill: rgb("#1976d2"), weight: "bold", size: 1.1em)[#it]
#show emph: it => text(fill: rgb("#1565c0"), style: "italic", size: 1.05em)[#it]

// Presentation title page
#align(center)[
  #v(1.5cm)
  #rect(
    fill: gradient.linear(rgb("#1976d2"), rgb("#42a5f5"), rgb("#90caf9")),
    width: 100%,
    inset: 3em,
    radius: 15pt,
    text(fill: white)[
      #text(size: 32pt, weight: "bold")[
        🎯 {title}
      ]
      #v(1.5cm)
      #text(size: 18pt, weight: "regular")[
        Presentation Document
      ]
    ]
  )
  
  #v(2cm)
  #text(size: 16pt, fill: rgb("#212121"))[
    *Presenter:* {author} \
    *Date:* {date} \
    *Format:* Slide-style PDF
  ]
  
  #v(1fr)
  #text(size: 10pt, style: "italic", fill: rgb("#757575"))[
    Professional presentations powered by WOT-PDF
  ]
]

#pagebreak()

// Presentation agenda/outline
#text(size: 22pt, weight: "bold", fill: rgb("#1976d2"))[
  📋 Agenda
]
#v(0.8em)
#rect(
  fill: gradient.linear(rgb("#1976d2"), rgb("#42a5f5")),
  width: 100%,
  height: 4pt,
  radius: 2pt
)
#v(1.5em)

#outline(
  title: none,
  depth: 2
)

#pagebreak()
