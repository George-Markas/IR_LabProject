from inverted_index import InvertedIndex
from typing import List, Tuple, Counter
import math

class VectorSpaceModel:
    """Vector space model using TF-IDF scoring"""

    def __init__(self, inverted_index: InvertedIndex):
        self.index = inverted_index
        self.idf_cache = {}

    def compute_idf(self, term: str) -> float:
        """ Compute IDF for a term"""
        if term not in self.idf_cache:
            df = self.index.get_doc_frequency(term)
            if df > 0:
                self.idf_cache[term] = math.log(self.index.total_docs / df)
            else:
                self.idf_cache[term] = 0

        return self.idf_cache[term]

    def compute_tf_idf(self, term: str, doc_id: str) -> float:
        """Compute TF-IDF score for a term in a document"""
        tf = self.index.get_term_frequency(term, doc_id)
        if tf == 0: return 0

        tf_normalized = 1 + math.log(tf)
        idf = self.compute_idf(term)
        return tf_normalized * idf

    def search(self, query_terms: List[str], top_n: int = 10) -> List[Tuple[str, float]]:
        """
        Search using cosine similarity with TF-IDF

        Args:
            query_terms (List[str]): List of query terms.
            top_n (int): Top n results to return. Defaults to 10.

        Returns:
            List of (doc_id, score) tuples.
        """

        if not query_terms:
            return []

        # Get candidate documents (union of all documents containing any query term)
        candidates = set()
        for term in query_terms:
            candidates.update(self.index.get_docs_containing(term))

        if not candidates:
            return []

        # Compute query vector using term frequency
        query_tf = Counter(query_terms)
        query_vector = {}
        query_norm = 0

        for term, freq in query_tf.items():
            tf_normalized = 1 + math.log(freq)
            idf = self.compute_idf(term)
            query_vector[term] = tf_normalized * idf
            query_norm += query_vector[term] ** 2

        query_norm = math.sqrt(query_norm)

        # Compute cosine similarity for each candidate document
        scores = []
        for doc_id in candidates:
            dot_product = 0
            doc_norm = 0

            # Only consider terms that appear in both query and document
            for term in query_terms:
                if term in query_terms:
                    doc_tfidf = self.compute_tf_idf(term, doc_id)
                    dot_product += query_vector[term] * doc_tfidf

            # Compute document norm
            for term, count in self.index.doc_terms[doc_id].items():
                doc_tfidf = self.compute_tf_idf(term, doc_id)
                doc_norm += doc_tfidf ** 2

            doc_norm = math.sqrt(doc_norm)

            # Cosine similarity
            if doc_norm > 0 and query_norm > 0:
                similarity = dot_product / (query_norm * doc_norm)
                scores.append((doc_id, similarity))

        # Sort by score and return the top n results
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_n]