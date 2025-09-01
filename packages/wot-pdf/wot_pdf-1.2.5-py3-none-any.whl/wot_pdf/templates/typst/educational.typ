// 🎯 WOT-PDF Educational Template
// Learning materials with engaging visual elements

#set document(title: "{title}", author: "{author}")
#set page(
  paper: "a4",
  margin: (left: 2.5cm, right: 2.5cm, top: 3cm, bottom: 3cm),
  numbering: "1",
  number-align: center,
  header: [
    #set text(size: 9pt, fill: rgb("#2e7d32"))
    #grid(
      columns: (1fr, 1fr),
      align: (left, right),
      [*{title}*], 
      [Learning Guide]
    )
    #line(length: 100%, stroke: 1pt + rgb("#4caf50"))
  ],
  footer: [
    #set text(size: 9pt, fill: rgb("#666666"))
    #line(length: 100%, stroke: 0.5pt + rgb("#4caf50"))
    #v(0.3em)
    #grid(
      columns: (1fr, 1fr),
      align: (left, right),
      [Educational Material], 
      context [Page #counter(page).display()]
    )
  ]
)

#set text(
  font: ("Segoe UI", "Arial"),
  size: 11pt,
  lang: "en"
)

#set heading(
  numbering: "Chapter 1:"
)

#show heading.where(level: 1): it => [
  #pagebreak(weak: true)
  #v(1em)
  #block(
    fill: gradient.linear(rgb("#2e7d32"), rgb("#4caf50")),
    width: 100%,
    inset: 1.2em,
    radius: 8pt,
    text(fill: white, weight: "bold", size: 18pt)[
      #counter(heading).display() #it.body
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
    inset: (left: 1em, top: 0.7em, bottom: 0.7em),
    radius: (right: 3pt),
    text(fill: rgb("#2e7d32"), weight: "bold", size: 14pt)[
      Section: #it.body
    ]
  )
  #v(0.8em)
]

#show heading.where(level: 3): it => [
  #v(1em)
  #text(fill: rgb("#2e7d32"), weight: "bold", size: 12pt)[
    📚 #it.body
  ]
  #v(0.5em)
]

// Learning objectives box
#let learning-objectives(content) = [
  #block(
    fill: rgb("#f3e5f5"),
    stroke: 2pt + rgb("#9c27b0"),
    width: 100%,
    inset: 1em,
    radius: 5pt,
    [
      #text(weight: "bold", size: 12pt, fill: rgb("#9c27b0"))[🎯 Learning Objectives]
      #v(0.5em)
      #content
    ]
  )
]

// Key points callout
#let key-point(content) = [
  #block(
    fill: rgb("#fff3e0"),
    stroke: 2pt + rgb("#ff9800"),
    width: 100%,
    inset: 1em,
    radius: 5pt,
    [
      #text(weight: "bold", size: 11pt, fill: rgb("#ff9800"))[💡 Key Point]
      #v(0.3em)
      #content
    ]
  )
]

// Exercise box
#let exercise(title, content) = [
  #v(1em)
  #block(
    fill: rgb("#e3f2fd"),
    stroke: 2pt + rgb("#2196f3"),
    width: 100%,
    inset: 1em,
    radius: 5pt,
    [
      #text(weight: "bold", size: 12pt, fill: rgb("#2196f3"))[✏️ Exercise: #title]
      #v(0.5em)
      #content
    ]
  )
  #v(1em)
]

// Code blocks with educational styling
#show raw.where(block: true): it => [
  #block(
    fill: rgb("#f5f5f5"),
    stroke: 1pt + rgb("#cccccc"),
    width: 100%,
    inset: 1em,
    radius: 5pt,
    above: 0.5em,
    below: 0.5em,
    [
      #text(fill: rgb("#2e7d32"), weight: "bold", size: 9pt)[CODE EXAMPLE]
      #v(0.3em)
      #text(font: ("SF Mono", "Consolas", "Monaco"), size: 10pt)[#it]
    ]
  )
]

// Lists with educational icons
#set list(
  indent: 1.2em, 
  marker: text(fill: rgb("#4caf50"))[▶]
)
#set enum(indent: 1.2em)

// Tables
#show table: it => [
  #v(0.8em)
  #block(
    stroke: 1pt + rgb("#4caf50"),
    radius: 3pt,
    width: 100%,
    it
  )
  #v(0.5em)
]

// Educational title page
#align(center)[
  #v(2cm)
  #block(
    fill: gradient.linear(rgb("#2e7d32"), rgb("#4caf50")),
    width: 100%,
    inset: 2em,
    radius: 15pt,
    text(fill: white)[
      #text(size: 26pt, weight: "bold")[
        📚 {title}
      ]
      #v(0.5cm)
      #text(size: 16pt)[
        Educational Learning Guide
      ]
    ]
  )
  
  #v(2cm)
  #block(
    fill: rgb("#e8f5e8"),
    stroke: 2pt + rgb("#4caf50"),
    width: 80%,
    inset: 1.5em,
    radius: 10pt,
    [
      #text(size: 14pt, fill: rgb("#2e7d32"))[
        *Instructor:* {author} \
        *Date:* {date} \
        *Course Material:* Interactive Learning
      ]
    ]
  )
  
  #v(1fr)
  #text(size: 10pt, style: "italic", fill: rgb("#666666"))[
    Educational content created with WOT-PDF Learning System
  ]
]

#pagebreak()

// Learning guide table of contents
#text(size: 18pt, weight: "bold", fill: rgb("#2e7d32"))[
  📖 Course Contents
]
#v(0.5em)
#line(length: 100%, stroke: 2pt + rgb("#4caf50"))
#v(1em)

#outline(
  title: none,
  depth: 3
)

#pagebreak()
