from src.search_engine.inverted_index import InvertedIndex
from typing import List

class BooleanRetrieval:
    """Boolean retrieval model"""

    def __init__(self, inverted_index: InvertedIndex):
        self.index = inverted_index

    def search(self, query_terms: List[str], operator: str = 'AND') -> List[str]:
        """
        Search using boolean operators.

        Args:
            query_terms (List[str]): List of query terms.
            operator (str, optional): 'AND', 'OR', 'NOT'. Defaults to 'AND'.

        Returns:
            List[str]: Matching documents.
        """

        if not query_terms:
            return []

        if operator == 'AND':
            # Intersection of all document sets
            result = self.index.get_docs_containing(query_terms[0])
            for term in query_terms[1:]:
                result = result.intersection(self.index.get_docs_containing(term))

            return list(result)
        elif operator == 'OR':
            # Union of all document sets
            result = set()
            for term in query_terms:
                result = result.union(self.index.get_docs_containing(term))

            return list(result)
        elif operator == 'NOT':
            # All documents minus the ones containing the terms
            all_docs = set(self.index.doc_lengths.keys())
            excluded = set()
            for term in query_terms:
                excluded = excluded.union(self.index.get_docs_containing(term))

            return list(all_docs - excluded)

        return []