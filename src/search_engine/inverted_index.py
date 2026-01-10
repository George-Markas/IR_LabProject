from collections import defaultdict, Counter
from typing import List, Dict, Set

class InvertedIndex:
    """Inverted index for document retrieval"""

    def __init__(self):
        self.index = defaultdict(list)
        self.doc_lengths = {}
        self.doc_terms = defaultdict(Counter)
        self.total_docs = 0
        self.avg_doc_length = 0

    def build(self, documents: Dict[str, List[str]]):
        """Build inverted index from processed documents"""
        self.total_docs = len(documents)
        total_length = 0

        for doc_id, terms in documents.items():
            doc_length = len(terms)
            self.doc_lengths[doc_id] = doc_length
            total_length += doc_length

            # Count term frequencies
            term_counts = Counter(terms)
            self.doc_terms[doc_id] = term_counts

            # Build inverted index with positions
            for pos, term in enumerate(terms):
                self.index[term].append((doc_id, pos))

            self.avg_doc_length = total_length / self.total_docs if self.total_docs > 0 else 0

    def get_docs_containing(self, term: str) -> Set[str]:
        """Get document IDs containing the given term"""
        return set(doc_id for doc_id, _ in self.index.get(term, []))

    def get_term_frequency(self, term: str, doc_id: str) -> int:
        """Get the frequency of a term in a document"""
        return self.doc_terms[doc_id].get(term, 0)

    def get_doc_frequency(self, term: str) -> int:
        """Get the number of documents containing the given term"""
        return len(set(doc_id for doc_id, _ in self.index.get(term, [])))