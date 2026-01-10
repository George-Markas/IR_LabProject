#show raw.where(block: false): it => box(
    fill: luma(230),
    inset: (x: 3pt, y: 0pt),
    outset: (y: 3pt),
    radius: 3pt,
    it,
)

#show raw.where(block: true): it => box(
    fill: luma(230),
    inset: (x: 3pt, y: 0pt),
    outset: (y: 5pt),
    radius: 3pt,
    it,
)

#show link: underline

#let title-page(title: [], authors: (), fill: yellow, body) = {
    set page(fill: rgb("#FFD700"), margin: (top: 1.5in, rest: 2in), paper: "a4", numbering: none)
    set text(font: "Source Sans 3", size: 14pt, spacing: 100%)

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
        #text(fill: blue, link(
            "https://colab.research.google.com/drive/1pvv89LXJCW1xzWn1KqJWVEXZrYChkZXH?usp=sharing",
        )[Colab])
        #h(0.3em)
        #text(fill: blue, link("https://github.com/George-Markas/IR_LabProject")[GitHub])
    ]

    align(bottom + left)[#datetime.today().display()]
    pagebreak()
    set par(
        first-line-indent: 1em,
        justify: false,
    )
    set page(fill: none, margin: auto, paper: "a4", numbering: "1")
    set heading(numbering: "1.")
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

= Συλλογή Δεδομένων
#v(1em)

Για τη μηχανή αναζήτησης χρησιμοποιείται το Reuters-21578 Corpus dataset. Το Reuters-21578
Corpus απαρτίζεται από έγγραφα που δημοσιεύτηκαν από το ειδησεογραφικό πρακτορείο
#text(fill: blue, link("https://en.wikipedia.org/wiki/Reuters")[Reuters]) το 1987.
To dataset συντάχθηκε από τον David D. Lewis, και έγινε διαθέσιμο για ερευνητικούς σκοπούς
στα τέλη του 1980.

Τα έγγραφα του dataset είναι άρθρα χρηματοοικονομικού χαρακτήρα, με το corpus να αποτελεί ένα
"στιγμιότυπο" της διεθνούς οικονομικής δραστηριότητας για το 1987. Κάθε έγγραφο περιέχει
διάφορα πεδία προς κατηγοριοποίηση:
#v(0.3em)
- `text` το κείμενο του άρθρου
- `topics` τα θέματα με τα οποία σχετίζεται το άρθρο
- `places` γεωγραφικές τοποθεσίες που αναφέρονται στο άρθρο
- `people` άτομα που αναφέρονται στο άρθρο
- `orgs` οργανισμοί που αναφέρονται στο άρθρο
- `exchanges` χρηματιστήρια που αναφέρονται στο άρθρο
- `date` η ημερομηνία δημοσίευσης του άρθρου
- `title` η επικεφαλίδα του άρθρου
#v(0.3em)
To Reuters-21578 Corpus dataset έχει διάφορες εκδοχές, για τις οποίες η κύρια
διαφοροποίηση είναι το υποσύνολο των δεδομένων που επιλέγεται. Το de facto standard
πλέον είναι η κατάτμηση ModApte, η οποία περιλαμβάνει έγγραφα με τουλάχιστον ένα θέμα
στο πεδίο `topics`.

To Reuters-21578 dataset έχει καθιερωθεί ως ένα από τα δημοφιλέστερα τεστ βαθμολόγησης
επιδόσεων στο πλαίσιο έρευνας κατηγοριοποίησης κειμένου. Έτσι, αποτελεί μια κλασσική
επιλογή dataset για τη μηχανή αναζήτησης μας.
#pagebreak()

= Προεπεξεργασία Κειμένου
#v(1em)

Ως προεπεξεργασία του κειμένου έγιναν οι εξής εργασίες:
#v(0.3em)
- Tokenization
- Stemming
- Stop-word removal
- Αφαίρεση ειδικών χαρακτήρων

== Tokenization
Tokenization είναι μία βασική διαδικασία στην επεξεργασία φυσικής γλώσσας κατά την οποία,
κείμενο κατακερματίζεται σε, πιο διαχειρίσιμα για μηχανές, tokens--λεκτικές μονάδες.
Ανάλογα με τον τύπο του tokenization, τα tokens μπορεί να είναι μεμονωμένοι χαρακτήρες,
λέξεις ή και φράσεις. Για παράδειγμα, κάνοντας tokenization λέξεων, η φράση `"Quis ut Deus?"`
θα γίνει `["Quis", "ut", "Deus"]`. Καθώς το Reuters-21578 Corpus dataset αποτελείται από άρθρα
γραμμένα στα Αγγλικά, μία γλώσσα με ξεκάθαρο διαχωρισμό των λέξεων, το tokenization σε επίπεδο
λέξεων είναι κατάλληλο από τη στιγμή που δεν απαιτούμε μεγάλη λεπτομέρεια κατά την
ανάλυση (όπως θα χρειαζόταν π.χ. για ορθογραφικό έλεγχο).

== Stemming
Stemming είναι η διαδικασία του να μειώνουμε μία λέξη στη "ρίζα" της, δηλαδή να αφαιρούμε
τυχόν προθέματα και παραθέματα. Για παράδειγμα, κάνοντας stemming για τη λέξη `most` θα έχουμε:
#v(0.3em)
#align(left)[
    - `"mostly"` #sym.arrow.r.long `"most"`\
    - `"utmost"` #sym.arrow.r.long `"most"`\
    - `"foremost"` #sym.arrow.r.long `"most"` _etc._
]
#v(0.3em)
Αυτή η "κανονικοποίηση" κάνει τη λεκτική ανάλυση πιο αποδοτική, όμως υπάρχουν πιθανά
μειονεκτήματα όπως η απώλεια ακρίβειας ή να γίνει το κείμενο πιο δυσανάγνωστο.

Υπάρχουν διάφοροι αλγόριθμοι stemming. Στη μηχανή αναζήτησης χρησιμοποιείται
ο #text(fill: blue, link("https://www.geeksforgeeks.org/nlp/porter-stemmer-technique-in-natural-language-processing/")[Stemmer του Porter]) καθώς
είναι ένας από τους δημοφιλέστερους αλγορίθμους stemming,
είναι γρήγορος και παρέχεται από την βιβλιοθήκη nltk.

== Stop-word removal
Stop-word removal είναι η διαδικασία αφαίρεσης λέξεων χαμηλής "σημασιολογικής αξίας"
από το κείμενο. Τέτοιες λέξεις είναι άρθρα, προθέσεις, αντωνυμίες etc. Για παράδειγμα,
η φράση `"One ring to rule them all"` μετά από stop-word removal θα γίνει
`"ring rule"`. Το όφελος είναι η βελτίωση της ακρίβειας και της απόδοσης εφαρμογών
επεξεργασίας φυσικής γλώσσας, ειδικά όταν ο όγκος του κειμένου προς επεξεργασία είναι μεγάλος.
Για τη μηχανή αναζήτησης, γίνεται αφαίρεση των stop-words που εμπεριέχονται στο σύνολο των
αγγλικών stop-words που παρέχεται από τη βιβλιοθήκη nltk.

== Αφαίρεση ειδικών χαρακτήρων
Η αφαίρεση ειδικών χαρακτήρων είναι ακριβώς αυτό που λέει το όνομα. Ομολογουμένως, ο όρος
"ειδικοί χαρακτήρες" δεν είναι ιδιαίτερα συγκεκριμένος. Μπορεί να σημαίνει μόνο το σύνολο ASCII, μόνο γράμματα (π.χ. και το ελληνικό αλφάβητο που απαιτεί κωδικοποίηση UTF-8) etc. Για τη μηχανή
αναζήτησης, "ειδικούς χαρακτήρες" θεωρούμε "μη αλφαριθμητικά", κοινώς οποιονδήποτε χαρακτήρα
κάνει τη μέθοδο ```py isalnum()``` να επιστρέψει ```py False``` για το εκάστοτε string. Η αφαίρεση
ειδικών χαρακτήρων γίνεται κυρίως για ευκολία. Προφανώς δε μπορούμε να ελέγξουμε το κείμενο του
Reuters-21578 Corpus "χειροκίνητα", οπότε αντί να υλοποιήσουμε κώδικα για τη διαχείριση των ειδικών
χαρακτήρων, απλά τους αφαιρούμε. Μειώνουμε έτσι και φόρτο για το πρόγραμμά μας.

= Indexing
#v(1em)
Για το ευρετήριο χρησιμοποιούμε τη δομή δεδομένων inverted index. Εντός της δομής αυτής,
το ευρετήριο οργανώνεται βάσει όρων, και κάθε όρος "δείχνει" σε μία λίστα εγγράφων
που περιέχουν τον όρο αυτό. Ουσιαστικά, το inverted index μοιάζει με
#text(fill: blue, link("https://en.wikipedia.org/wiki/Hash_table")[hash table]) από την άποψη
πως έχουμε συνδυασμό "κλειδιού - στοιχείου", όπου το κλειδί είναι ο όρος και το στοιχείο είναι
λίστα από έγγραφα.

Η υλοποίηση inverted index για τη μηχανή αναζήτησης βασίζεται στο ```py dict()``` container
της python, που αποθηκεύει πληροφορία με το προαναφερθέν μοτίβο "κλειδιού  - στοιχείου".
Παράδειγμα dictionary:
#v(0.5em)
#align(center)[
    ```py
    car_dict = {
        "model": "R8",
        "make": "Audi",
        "year": 2006
    }
    ```
]
#v(1em)

Κάθε έγγραφο είναι ένα dictionary που περιέχει ένα _id_ και μία λίστα από όρους.
Συγκεκριμένα: ```py documents: Dict[str, List[str]]```

Έτσι, έχουμε την ακόλουθη επανάληψη για να επεξεργαζόμαστε τα στοιχεία κάθε dictionary:
#v(0.3em)
#align(center)[
    ```py
    for doc_id, terms in documents.items():
    ```
]
#v(1em)

- Καταγράφουμε πόσους όρους έχει το έγγραφο (και κατ' επέκταση τους συνολικούς όρους του dataset):
#v(0.3em)
#align(center)[
    ```py
    doc_length = len(terms)
    self.doc_lengths[doc_id] = doc_length
    total_length += doc_length
    ```
]
#v(1em)

- Καταγράφουμε τη συχνότητα των όρων:
#v(0.3em)
#align(center)[
    ```py
    term_counts = Counter(terms)
    self.doc_terms[doc_id] = term_counts
    ```
]
#v(1em)

- Tέλος, κατασκευάζουμε το ευρετήριο, καταχωρούμε δηλαδή σε λίστα τη θέση του
    εκάστοτε όρου και το αντίστοιχο _id_ του εγγράφου:

#v(0.3em)
#align(center)[
    ```py
    for pos, term in enumerate(terms):
        self.index[term].append((doc_id, pos))
    ```
]
#v(1em)

Η μέθοδος ```py enumerate()``` αναθέτει δείκτες στα στοιχεία της δοθείσας λίστας
για εύκολη προσπέλαση. Παράδειγμα:
#v(0.3em)
#align(center)[
    ```py
    s = ["foo", "bar", "baz"]
    print(list(enumerate(s)))
    ```
    #v(0.8em)
    _Output:_
    ```py [(0, 'foo'), (1, 'bar'), (2, 'baz')]```
]
#v(1em)
#pagebreak()

Το inverted index class έχει getter methods για να επιστρέφουμε τα εξής:

- Έγγραφα που περιέχουν συγκεκριμένο όρο
#v(0.3em)
#align(center)[
    ```py
    def get_docs_containing(self, term: str) -> Set[str]:
        return set(doc_id for doc_id, _ in self.index.get(term, []))
    ```
]
#v(1em)

- Τη συχνότητα ενός όρου
#v(0.3em)
#align(center)[
    ```py
    def get_term_frequency(self, term: str, doc_id: str) -> int:
        return self.doc_terms[doc_id].get(term, 0)
    ```
]
#v(1em)

- Τη συχνότητα εγγράφων για έναν όρο, δηλαδή σε πόσα έγγραφα 
  εμπεριέχεται ο όρος αυτός
#v(0.3em)
#align(center)[
    #set text(size: 13pt)
    ```py
    def get_doc_frequency(self, term: str) -> int:
        return len(set(doc_id for doc_id, _ in self.index.get(term, [])))
    ```
]
#v(1em)