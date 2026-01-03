from src.search_engine.inverted_index import InvertedIndex
from typing import List, Tuple
import math

class OkapiBM25:
    """Okapi BM25 probabilistic retrieval model"""

    def __init__(self, inverted_index: InvertedIndex, k1: float = 1.5, b: float = 0.75):
        self.index = inverted_index
        self.k1 = k1  # Term frequency saturation parameter
        self.b = b  # Length normalization parameter
        self.idf_cache = {}

    def compute_idf(self, term: str) -> float:
        if term not in self.idf_cache:
            df = self.index.get_doc_frequency(term)
            n = self.index.total_docs
            if df > 0:
                # BM25 IDF formula
                self.idf_cache[term] = math.log((n - df + 0.5) / (df + 0.5) + 1)
            else:
                self.idf_cache[term] = 0
        return self.idf_cache[term]


    def compute_bm25_score(self, term: str, doc_id: str) -> float:
        """Compute BM25 score for a term in a document"""
        tf = self.index.get_term_frequency(term, doc_id)
        if tf == 0: return 0

        doc_length = self.index.doc_lengths[doc_id]
        avg_length = self.index.avg_doc_length

        # BM25 formula
        idf = self.compute_idf(term)
        numerator = tf * (self.k1 + 1)
        denominator = tf + self.k1 * (1 - self.b + self.b * (doc_length / avg_length))

        return idf * (numerator / denominator)

    def search(self, query_terms: List[str], top_n: int = 10) -> List[Tuple[str, float]]:
        """
        Search using BM25 scoring.

        Args:
            query_terms (List[str]): List of query terms.
            top_n (int): Top n results to return. Defaults to 10.

        Returns:
            List of (doc_id, score) tuples.
        """

        if not query_terms:
            return []

        # Get candidate documents
        candidates = set()
        for term in query_terms:
            candidates.update(self.index.get_docs_containing(term))

        if not candidates:
            return []

        # Compute BM25 score for each candidate
        scores = []
        for doc_id in candidates:
            score = 0
            for term in query_terms:
                score += self.compute_bm25_score(term, doc_id)

            scores.append((doc_id, score))

        # Sort by score and return top n results
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_n]