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

Για τη μηχανή αναζήτησης χρησιμοποιείται το Reuters-21578 Corpus dataset. Το Reuters-21578
Corpus απαρτίζεται από έγγραφα που δημοσιεύτηκαν από το ειδησεογραφικό πρακτορείο Reuters @reuters-wiki το 1987.To dataset συντάχθηκε από τον David D. Lewis, και έγινε διαθέσιμο για ερευνητικούς σκοπούς στα τέλη του 1980.

Τα έγγραφα του dataset είναι άρθρα χρηματοοικονομικού χαρακτήρα, με το corpus να αποτελεί ένα
"στιγμιότυπο" της διεθνούς οικονομικής δραστηριότητας για το 1987. Κάθε έγγραφο περιέχει
διάφορα πεδία προς κατηγοριοποίηση:

- `text` το κείμενο του άρθρου
- `topics` τα θέματα με τα οποία σχετίζεται το άρθρο
- `places` γεωγραφικές τοποθεσίες που αναφέρονται στο άρθρο
- `people` άτομα που αναφέρονται στο άρθρο
- `orgs` οργανισμοί που αναφέρονται στο άρθρο
- `exchanges` χρηματιστήρια που αναφέρονται στο άρθρο
- `date` η ημερομηνία δημοσίευσης του άρθρου
- `title` η επικεφαλίδα του άρθρου

To Reuters-21578 Corpus dataset έχει διάφορες εκδοχές, για τις οποίες η κύρια
διαφοροποίηση είναι το υποσύνολο των δεδομένων που επιλέγεται. Το de facto standard
πλέον είναι η κατάτμηση ModApte, η οποία περιλαμβάνει έγγραφα με τουλάχιστον ένα θέμα
στο πεδίο `topics`.

To Reuters-21578 dataset έχει καθιερωθεί ως ένα από τα δημοφιλέστερα τεστ βαθμολόγησης
επιδόσεων στο πλαίσιο έρευνας κατηγοριοποίησης κειμένου. Έτσι, αποτελεί μια κλασσική
επιλογή dataset για τη μηχανή αναζήτησης μας.
#pagebreak()

= Προεπεξεργασία Κειμένου

Ως προεπεξεργασία του κειμένου έγιναν οι εξής εργασίες:

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
#align(left)[
  - `"mostly"` #sym.arrow.r.long `"most"`\
  - `"utmost"` #sym.arrow.r.long `"most"`\
  - `"foremost"` #sym.arrow.r.long `"most"` _etc._
]

Αυτή η "κανονικοποίηση" κάνει τη λεκτική ανάλυση πιο αποδοτική, όμως υπάρχουν πιθανά
μειονεκτήματα όπως η απώλεια ακρίβειας ή να γίνει το κείμενο πιο δυσανάγνωστο.

Υπάρχουν διάφοροι αλγόριθμοι stemming. Στη μηχανή αναζήτησης χρησιμοποιείται
ο Stemmer του Porter @porter-stemmer καθώς είναι ένας από τους δημοφιλέστερους αλγορίθμους
stemming, είναι γρήγορος και παρέχεται από την βιβλιοθήκη nltk.

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
"ειδικοί χαρακτήρες" δεν είναι ιδιαίτερα συγκεκριμένος. Μπορεί να σημαίνει μόνο το σύνολο ASCII,
μόνο γράμματα (π.χ. και το ελληνικό αλφάβητο που απαιτεί κωδικοποίηση UTF-8) etc. Για τη μηχανή
αναζήτησης, "ειδικούς χαρακτήρες" θεωρούμε "μη αλφαριθμητικά", κοινώς οποιονδήποτε χαρακτήρα
κάνει τη μέθοδο ```py isalnum()``` να επιστρέψει ```py False``` για το εκάστοτε string. Η αφαίρεση
ειδικών χαρακτήρων γίνεται κυρίως για ευκολία. Προφανώς δε μπορούμε να ελέγξουμε το κείμενο του
Reuters-21578 Corpus "χειροκίνητα", οπότε αντί να υλοποιήσουμε κώδικα για τη διαχείριση των ειδικών
χαρακτήρων, απλά τους αφαιρούμε. Μειώνουμε έτσι και φόρτο για το πρόγραμμά μας.

= Indexing
Για το ευρετήριο χρησιμοποιούμε τη δομή δεδομένων inverted index. Εντός της δομής αυτής,
το ευρετήριο οργανώνεται βάσει όρων, και κάθε όρος "δείχνει" σε μία λίστα εγγράφων
που περιέχουν τον όρο αυτό. Ουσιαστικά, το inverted index μοιάζει με
hash table @hash-table-wiki από την άποψη πως έχουμε συνδυασμό "κλειδιού - στοιχείου",
όπου το κλειδί είναι ο όρος και το στοιχείο είναι λίστα από έγγραφα.

Η υλοποίηση inverted index για τη μηχανή αναζήτησης βασίζεται στο ```py dict()``` container
της python, που αποθηκεύει πληροφορία με το προαναφερθέν μοτίβο "κλειδιού  - στοιχείου".
Παράδειγμα dictionary:
#align(center)[
  ```py
  car_dict = {
      "model": "R8",
      "make": "Audi",
      "year": 2006
  }
  ```
]

#set par(first-line-indent: 0em)

Κάθε έγγραφο είναι ένα dictionary που περιέχει ένα _id_ και μία λίστα από όρους.
Συγκεκριμένα: ```py documents: Dict[str, List[str]]```

Έτσι, έχουμε την ακόλουθη επανάληψη για να επεξεργαζόμαστε τα στοιχεία κάθε dictionary:

#align(center)[
  ```py
  for doc_id, terms in documents.items():
  ```
]
#v(0.5em)


- Καταγράφουμε πόσους όρους έχει το έγγραφο (και κατ' επέκταση τους συνολικούς όρους του dataset):
#align(center)[
  ```py
  doc_length = len(terms)
  self.doc_lengths[doc_id] = doc_length
  total_length += doc_length
  ```
]
#v(0.5em)

- Καταγράφουμε τη συχνότητα των όρων:

#align(center)[
  ```py
  term_counts = Counter(terms)
  self.doc_terms[doc_id] = term_counts
  ```
]
#v(0.5em)

- Tέλος, κατασκευάζουμε το ευρετήριο, καταχωρούμε δηλαδή σε λίστα τη θέση του
  εκάστοτε όρου και το αντίστοιχο _id_ του εγγράφου:
#align(center)[
  ```py
  for pos, term in enumerate(terms):
      self.index[term].append((doc_id, pos))
  ```
]
#v(0.5em)

Η μέθοδος ```py enumerate()``` αναθέτει δείκτες στα στοιχεία της δοθείσας λίστας
για εύκολη προσπέλαση. Παράδειγμα:
#align(center)[
  ```py
  s = ["foo", "bar", "baz"]
  print(list(enumerate(s)))
  ```
  #v(0.5em)
  _Output:_
  ```py [(0, 'foo'), (1, 'bar'), (2, 'baz')]```
]



Το inverted index class έχει getter methods για να επιστρέφουμε τα εξής:

- Έγγραφα που περιέχουν συγκεκριμένο όρο
#align(center)[
  ```py
  def get_docs_containing(self, term: str) -> Set[str]:
      return set(doc_id for doc_id, _ in self.index.get(term, []))
  ```
]
#v(0.5em)


- Τη συχνότητα ενός όρου
#align(center)[
  ```py
  def get_term_frequency(self, term: str, doc_id: str) -> int:
      return self.doc_terms[doc_id].get(term, 0)
  ```
]
#v(0.5em)
#pagebreak()

- Τη συχνότητα εγγράφων για έναν όρο, δηλαδή σε πόσα έγγραφα
  εμπεριέχεται ο όρος αυτός
#align(center)[
  #set text(size: 13pt)
  ```py
  def get_doc_frequency(self, term: str) -> int:
      return len(set(doc_id for doc_id, _ in self.index.get(term, [])))
  ```
]
#v(0.5em)

= Μηχανή Αναζήτησης
Η υλοποίηση της μηχανής αναζήτησης κάνει χρήση των τριών προτεινόμενων μοντέλων της εκφώνησης:
- Boolean Retrieval
- Vector Space Model
- Okapi BM25

== Boolean Retrieval
Αυτό το μοντέλο ανάκτησης βασίζεται στις γνωστές λογικές πράξεις Boole. Στη μηχανή αναζήτησης
υλοποιούνται οι εξής:
- *AND* -- επιστρέφονται έγγραφα που περιέχουν *όλους* τους όρους από το query του χρήστη
- *OR* -- επιστρέφονται έγγραφα που περιέχουν *τουλάχιστον έναν* από τους όρους από το query
  του χρήστη
- *NOT* -- επιστρέφονται έγγραφα που *δεν* περιέχουν όρους από το query του χρήστη
Το μοντέλο Boolean Retrieval λειτουργεί ταιριάζοντας ακριβώς τα έγγραφα βάσει του query του
χρήστη και της λογικής πράξης που επιλέχθηκε. Συνεπώς, δεν υπάρχει νόημα κατάταξης των αποτελεσμάτων,
το έγγραφο είτε επιστρέφεται είτε όχι.

== Vector Space Model
Στο αυτό το μοντέλο, τα έγγραφα και τα queries αναπαριστώνται ως διανύσματα σε
πολυδιάστατο χώρο. Κάθε διάσταση αντιστοιχεί σε συγκεκριμένο όρο από το dataset.
- Κάθε έγγραφο / query γίνεται $Ν$-διάστατο διάνυσμα, όπου $Ν$ είναι ο αριθμός ξεχωριστών όρων
  στο dataset.

- Κάθε διανυσματική συνιστώσα αναπαριστά το βάρος (σημασία) του συγκεκριμένου όρου εντός
  του εγγράφου / query.

=== Βαθμολόγηση TF-IDF
Η φόρμουλα TF-IDF (Term Frequency-Inverse Document Frequency) χρησιμοποιείται για τον
υπολογισμό του βάρους κάθε όρου εντός ενός εγγράφου.

=== Term Frequency (TF)
To Term Frequency είναι το πόσο συχνά εμφανίζεται ένας όρος στο έγγραφο:
#align(center)[
  #set text(size: 16pt)
  $ t f_(i,j) = n_(i,j) / (sum_(k) n_(k,j)) $
]

=== Cosine Similarity
Προκειμένου να υπολογίσουμε την ομοιότητα μεταξύ ενός διανύσματος query και ενός
διανύσματος εγγράφου, χρησιμοποιούμε τον εξής τύπο:
#align(center)[
  #set text(size: 16pt)
  $
    cos(a, b) = (sum_(i=1)^n a_(i) b_(i)) /
    sqrt(sum_(i=1)^n a^2_(i) sum_(i=1)^n b^2_(i))
  $
]

Τα βάρη διακυμαίνονται από 0 εώς 1, με την ομοιότητα να αυξάνεται όσο το βάρος
πλησιάζει το 1.

== Πιθανοτικό Μοντέλο Okapi BM25
Το μοντέλο Okapi BM25 (Best Matching 25) είναι μία βελτιωμένη εκδοχή του TF-IDF.
Λειτουργεί υπολογίζοντας score ομοιότητας μεταξύ ενός query $q$ και ενός εγγράφου $d$,
χρησιμοποιώντας Term Frequency (TF), Inverse Document Frequency (IDF) και
Document Length Normalization (κανονικοποιεί το score ομοιότητας για μεγαλύτερα
έγγραφα έτσι ώστε να μη συσσωρεύονται στη κορυφή της κατάταξης).

=== Κανονικοποίηση Term Frequency (TF)
Το Term Frequency κανονικοποιείται με την ακόλουθη φόρμουλα, με αποτέλεσμα, από ένα
σημείο και μετά, οι επιπρόσθετες εμφανίσεις ενός όρου να συνεισφέρουν όλο και λιγότερο
στο score ομοιότητας του εγγράφου:
#align(center)[
  #set text(size: 16pt)
  $
    T F_(t,d) = (f r e q(t,d)) /
    (f r e q(t,d) + k_(1) dot (1 - b + b dot abs(d) / "avgdl"))
  $
]
#pagebreak()

- *$t$*: όρος query,
- *$d$*: έγγραφο,
- *$f r e q(t,d)$*: πόσες φορές ο όρος $t$ εμφανίζεται στο έγγραφο $d$,
- *$abs(d)$*: μήκος του εγγράφου $d$,
- *$"avgdl"$*: μέσο μήκος εγγράφου στο dataset,
- *$k_(1)$*: σταθερά αύξησης της συχνότητας όρων,
- *$b$*: σταθερά κανονικοποίησης μήκους εγγράφων,

=== Inverse Document Frequency (IDF)
To Ιnverse Document Frequency είναι σημασία ενός όρου σε όλο το dataset:
#align(center)[
  #set text(size: 16pt)
  $I D F(t) = log((N - n_(t) + 0.5) / (n_(t) + 0.5))$
]

=== Τελικός υπολογισμός score
#align(center)[
  #set text(size: 16pt)
  $S c o r e(q, d) = sum_(t in q) I D F(t) dot T F(t,d)$
]

Για την υλοποίηση του αλγορίθμου στη μηχανή αναζήτησης, εφαρμόστηκαν οι παραπάνω τύποι
με τη βοήθεια της βιβλιοθήκης math:

- IDF:
#align(center)[
  #set text(size: 12pt)
  ```py
  def compute_idf(self, term: str) -> float:
      if term not in self.idf_cache:
      df = self.index.get_doc_frequency(term)
      n = self.index.total_docs
      if df > 0:
          self.idf_cache[term] = math.log((n - df + 0.5) / (df + 0.5) + 1)
      else:
          self.idf_cache[term] = 0
      return self.idf_cache[term]

  ```
]

- Score (και TF):
#align(center)[
  #set text(size: 11pt)
  ```py
  def compute_bm25_score(self, term: str, doc_id: str) -> float:
      tf = self.index.get_term_frequency(term, doc_id)
      if tf == 0: return 0

      doc_length = self.index.doc_lengths[doc_id]
      avg_length = self.index.avg_doc_length

      idf = self.compute_idf(term)
      numerator = tf * (self.k1 + 1)
      denominator = tf + self.k1 * (1 - self.b + self.b * (doc_length / avg_length))

      return idf * (numerator / denominator)
  ```
]
#v(0.5em)

= Αξιολόγηση συστήματος
Μαζί με το Reuters-21578 Corpus, για την αξιολόγηση της μηχανής αναζήτησης χρησιμοποιήθηκε
και το CISI dataset.

== Μετρήσεις αξιολόγησης
- Precision
- Recall
- F1-Score
- Average Precision

=== Precision (P)
Precision είναι το ποσοστό σχετικών εγγράφων από εκείνα που επιστράφηκαν:

#align(center)[
  $
    "Precision" = "True Positives" / ("True Positives"+ "False Positives")
  $
]

=== Recall (R)
Recall είναι το ποσοστό των σχετικών εγγράφων που επιστράφηκαν:
#align(center)[
  $ "Recall" = "True Positives" / ("True Positives" + "False Negatives") $
]

=== F1-Score (F1)
F1-Score είναι ο αρμονικός μέσος @harmonic-mean-wiki Precision και Recall:

#align(center)[
  $"F1-Score" = 2 dot ("Precision" dot "Recall") / ("Precision" + "Recall")$
]
#v(1em)

#list(
  marker: [‣],
  [True Positives: τα σχετικά έγγραφα που επιστράφηκαν],
  [False Positives: τα μη-σχετικά έγγραφα που επιστράφηκαν],
  [False Negatives: τα σχετικά έγγραφα που δεν επιστράφηκαν],
)
#pagebreak()


== Αποτελέσματα αξιολόγησης
#v(1em)

*Reuters-21578 Corpus*
#table(
  columns: 5,
  fill: (_, y) => if y == 0 { gray.lighten(75%) },
  align: (left, center, center, center, center),
  table.header([*Method*], [*Precision*], [*Recall*], [*F1-Score*], [*Avg. Precision*]),
  [BOOLEAN], [N/A], [N/A], [N/A], [N/A],
  [VSM], [0.3200], [0.0320], [0.0582], [0.0278],
  [BM25], [0.3200], [0.0320], [0.0582], [0.0244],
)

#v(1em)

*CISI*
#table(
  columns: 5,
  fill: (_, y) => if y == 0 { gray.lighten(75%) },
  align: (left, center, center, center, center),
  table.header([*Method*], [*Precision*], [*Recall*], [*F1-Score*], [*Avg. Precision*]),
  [BOOLEAN], [N/A], [N/A], [N/A], [N/A],
  [VSM], [0.3000], [0.1109], [0.1426], [0.0617],
  [BM25], [0.3200], [0.1192], [0.1544], [0.1058],
)

#v(0.5em)

Παρατηρούμε πως το Precision μεταξύ των δύο datasets είναι σχεδόν πανομοιότυπο,
αλλά το Recall και το F1-Score είναι σαφώς υψηλότερα για το CISI. Αυτό μάλλον
οφείλεται στο γεγονός πως χρησιμοποιούμε ολόκληρο το CISI, ενώ από το Reuters-21578 Corpus
παίρνουμε sample size 1000 εγγράφων. Επίσης, τα test queries για το CISI είναι πολύ
μεγαλύτερα καθώς τα παίρνουμε έτοιμα από το _CISI.QRY_ αρχείο του dataset, ενώ για το
Reuters-21578 Corpus χρησιμοποιούμε ενδεικτικά κάποιες κατηγορίες όπως
`"acq"`, `"crude"`, `"money-fx"` etc.

#bibliography("assets/references.yaml", title: "Αναφορές")
