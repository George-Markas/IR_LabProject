#let title-page(title: [], authors: (), fill: yellow, body) = {
    set page(fill: rgb("#FFD700"), margin: (top: 1.5in, rest: 2in))
    set text(font: "Source Sans 3", size: 14pt)
    set heading(numbering: "1.1.1")
    line(start: (0%, 0%), end: (8.5in, 0%), stroke: (thickness: 2pt))
    align(horizon + left)[
        #text(size: 24pt, title)\
        #v(1em)
        Εργασία 2025-2026
        #v(2em)
        #for author in authors [
            #author.name, AM: #author.am \
        ]
    ]

    align(bottom)[
        #show link: underline
        #text(fill: blue, link("https://colab.research.google.com/drive/1pvv89LXJCW1xzWn1KqJWVEXZrYChkZXH?usp=sharing")[Colab])
        #h(0.3em)
        #text(fill: blue, link("https://github.com/George-Markas/IR_LabProject")[GitHub])
    ]

    align(bottom + left)[#datetime.today().display()]
    pagebreak()
    set page(fill: none, margin: auto)
    align(horizon, outline(indent: auto, title: "Περιεχόμενα"))
    pagebreak()
    body
}

#show: body => title-page(
    title: [Ανάκτηση Πληροφορίας],
    authors: (
        (name: "Αντιβάχης Αντώνιος", am: [22390289]),
        (name: "Μαρκαντωνάτος Γεώργιος", am: [22390138]),
    ),
    body,
)