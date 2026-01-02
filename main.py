"""
Reuters-21578 Search Engine with Multiple Retrieval Algorithms
Implements Boolean, Vector Space Model (TF-IDF), and BM25 retrieval
"""

import nltk
from nltk.corpus import reuters
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from collections import defaultdict, Counter
import math
import numpy as np
from typing import List, Dict, Set, Tuple

# Download required NLTK data
try:
    reuters.fileids()
except:
    nltk.download('reuters')
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('punkt_tab')

class TextProcessor:
    """Handles text preprocessing: tokenization, stemming, stop word removal"""

    def __init__(self):
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))

    def process(self, text: str) -> List[str]:
        """Process text: lowercase, tokenize, remove stopwords, stem"""
        # Lowercase and tokenize
        tokens = word_tokenize(text.lower())

        # Remove non-alphanumeric tokens and stopwords
        tokens = [token for token in tokens
                  if token.isalnum() and token not in self.stop_words]

        # Stem tokens
        tokens = [self.stemmer.stem(token) for token in tokens]

        return tokens

class InvertedIndex:
    """Inverted index for efficient document retrieval"""

    def __init__(self):
        self.index = defaultdict(list)  # term -> [(doc_id, positions)]
        self.doc_lengths = {}  # doc_id -> length
        self.doc_terms = defaultdict(Counter)  # doc_id -> {term: count}
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
        """Get all document IDs containing the term"""
        return set(doc_id for doc_id, _ in self.index.get(term, []))

    def get_term_freq(self, term: str, doc_id: str) -> int:
        """Get term frequency in a document"""
        return self.doc_terms[doc_id].get(term, 0)

    def get_doc_freq(self, term: str) -> int:
        """Get document frequency (number of docs containing term)"""
        return len(set(doc_id for doc_id, _ in self.index.get(term, [])))

class BooleanRetrieval:
    """Boolean retrieval model with AND, OR, NOT operations"""

    def __init__(self, inverted_index: InvertedIndex):
        self.index = inverted_index

    def search(self, query_terms: List[str], operator: str = 'AND') -> List[str]:
        """
        Search using boolean logic
        operator: 'AND', 'OR', or 'NOT'
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
            # All docs minus docs containing the terms
            all_docs = set(self.index.doc_lengths.keys())
            excluded = set()
            for term in query_terms:
                excluded = excluded.union(self.index.get_docs_containing(term))
            return list(all_docs - excluded)

        return []

class VectorSpaceModel:
    """Vector Space Model using TF-IDF scoring"""

    def __init__(self, inverted_index: InvertedIndex):
        self.index = inverted_index
        self.idf_cache = {}

    def compute_idf(self, term: str) -> float:
        """Compute IDF for a term"""
        if term not in self.idf_cache:
            df = self.index.get_doc_freq(term)
            if df > 0:
                self.idf_cache[term] = math.log(self.index.total_docs / df)
            else:
                self.idf_cache[term] = 0
        return self.idf_cache[term]

    def compute_tf_idf(self, term: str, doc_id: str) -> float:
        """Compute TF-IDF score for a term in a document"""
        tf = self.index.get_term_freq(term, doc_id)
        if tf == 0:
            return 0

        # Use log normalization for TF
        tf_normalized = 1 + math.log(tf)
        idf = self.compute_idf(term)
        return tf_normalized * idf

    def search(self, query_terms: List[str], top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Search using cosine similarity with TF-IDF
        Returns: List of (doc_id, score) tuples
        """
        if not query_terms:
            return []

        # Get candidate documents (union of all docs containing any query term)
        candidates = set()
        for term in query_terms:
            candidates.update(self.index.get_docs_containing(term))

        if not candidates:
            return []

        # Compute query vector (using simple term frequency)
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
                if term in query_vector:
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

        # Sort by score and return top k
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

class BM25:
    """Okapi BM25 probabilistic retrieval model"""

    def __init__(self, inverted_index: InvertedIndex, k1: float = 1.5, b: float = 0.75):
        self.index = inverted_index
        self.k1 = k1  # Term frequency saturation parameter
        self.b = b    # Length normalization parameter
        self.idf_cache = {}

    def compute_idf(self, term: str) -> float:
        """Compute IDF for BM25"""
        if term not in self.idf_cache:
            df = self.index.get_doc_freq(term)
            n = self.index.total_docs
            if df > 0:
                # BM25 IDF formula
                self.idf_cache[term] = math.log((n - df + 0.5) / (df + 0.5) + 1)
            else:
                self.idf_cache[term] = 0
        return self.idf_cache[term]

    def compute_bm25_score(self, term: str, doc_id: str) -> float:
        """Compute BM25 score for a term in a document"""
        tf = self.index.get_term_freq(term, doc_id)
        if tf == 0:
            return 0

        doc_length = self.index.doc_lengths[doc_id]
        avg_length = self.index.avg_doc_length

        # BM25 formula
        idf = self.compute_idf(term)
        numerator = tf * (self.k1 + 1)
        denominator = tf + self.k1 * (1 - self.b + self.b * (doc_length / avg_length))

        return idf * (numerator / denominator)

    def search(self, query_terms: List[str], top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Search using BM25 scoring
        Returns: List of (doc_id, score) tuples
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

        # Sort by score and return top k
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]

class SearchEngine:
    """Main search engine class"""

    def __init__(self):
        self.processor = TextProcessor()
        self.inverted_index = InvertedIndex()
        self.boolean_retrieval = None
        self.vsm = None
        self.bm25 = None
        self.raw_documents = {}  # Store raw text for display
        self.processed_documents = {}

    def build_index(self, sample_size: int = 1000):
        """Build index from Reuters corpus"""
        print(f"Loading Reuters corpus (sample size: {sample_size})...")

        # Get file IDs (limit for faster demo)
        fileids = reuters.fileids()[:sample_size]

        print(f"Processing {len(fileids)} documents...")
        for fileid in fileids:
            # Get raw text
            raw_text = reuters.raw(fileid)
            self.raw_documents[fileid] = raw_text

            # Process text
            processed = self.processor.process(raw_text)
            self.processed_documents[fileid] = processed

        print("Building inverted index...")
        self.inverted_index.build(self.processed_documents)

        # Initialize retrieval models
        self.boolean_retrieval = BooleanRetrieval(self.inverted_index)
        self.vsm = VectorSpaceModel(self.inverted_index)
        self.bm25 = BM25(self.inverted_index)

        print(f"Index built successfully!")
        print(f"Total documents: {self.inverted_index.total_docs}")
        print(f"Vocabulary size: {len(self.inverted_index.index)}")
        print(f"Average document length: {self.inverted_index.avg_doc_length:.2f} terms")

    def search(self, query: str, method: str = 'bm25', top_k: int = 10,
               boolean_op: str = 'AND') -> List[Tuple[str, float]]:
        """
        Search for documents matching the query

        Args:
            query: Search query string
            method: 'boolean', 'vsm', or 'bm25'
            top_k: Number of results to return (for ranked methods)
            boolean_op: Boolean operator for boolean retrieval ('AND', 'OR', 'NOT')

        Returns:
            List of (doc_id, score) tuples
        """
        # Process query
        query_terms = self.processor.process(query)

        if not query_terms:
            return []

        # Execute search based on method
        if method == 'boolean':
            doc_ids = self.boolean_retrieval.search(query_terms, boolean_op)
            # Boolean doesn't rank, so assign score of 1.0
            return [(doc_id, 1.0) for doc_id in doc_ids[:top_k]]

        elif method == 'vsm':
            return self.vsm.search(query_terms, top_k)

        elif method == 'bm25':
            return self.bm25.search(query_terms, top_k)

        else:
            raise ValueError(f"Unknown method: {method}")

    def display_results(self, results: List[Tuple[str, float]], query: str,
                        method: str, max_length: int = 200):
        """Display search results in a user-friendly format"""
        print(f"\n{'='*80}")
        print(f"Query: '{query}'")
        print(f"Method: {method.upper()}")
        print(f"Found {len(results)} documents")
        print(f"{'='*80}\n")

        for rank, (doc_id, score) in enumerate(results, 1):
            raw_text = self.raw_documents.get(doc_id, "")

            # Truncate for display
            preview = raw_text[:max_length].replace('\n', ' ')
            if len(raw_text) > max_length:
                preview += "..."

            print(f"{rank}. Document: {doc_id}")
            print(f"   Score: {score:.4f}")
            print(f"   Preview: {preview}")
            print(f"   Categories: {', '.join(reuters.categories(doc_id))}")
            print()

class SearchEvaluator:
    """Evaluate search engine performance"""

    def __init__(self, search_engine: SearchEngine):
        self.engine = search_engine

    @staticmethod
    def create_test_queries() -> List[Tuple[str, Set[str]]]:
        """
        Create test queries with relevance judgments
        Returns: List of (query, relevant_doc_ids) tuples
        """
        # Create queries based on Reuters categories
        test_queries = []

        # Sample some categories
        categories = ['acq', 'earn', 'crude', 'trade', 'money-fx']

        for category in categories:
            # Get documents in this category
            relevant_docs = set(reuters.fileids(category)[:100])

            if relevant_docs:
                # Create a query based on category name
                query = category.replace('-', ' ')
                test_queries.append((query, relevant_docs))

        return test_queries

    def evaluate(self, query: str, relevant_docs: Set[str],
                 method: str, top_k: int = 10) -> Dict[str, float]:
        """
        Evaluate a single query
        Returns: Dictionary with precision, recall, F1, and AP
        """
        # Get search results
        results = self.engine.search(query, method=method, top_k=top_k)
        retrieved_docs = set(doc_id for doc_id, _ in results)

        # Calculate metrics
        true_positives = len(retrieved_docs.intersection(relevant_docs))

        precision = true_positives / len(retrieved_docs) if retrieved_docs else 0
        recall = true_positives / len(relevant_docs) if relevant_docs else 0

        f1 = (2 * precision * recall / (precision + recall)
              if (precision + recall) > 0 else 0)

        # Calculate Average Precision
        ap = 0
        relevant_found = 0
        for rank, (doc_id, _) in enumerate(results, 1):
            if doc_id in relevant_docs:
                relevant_found += 1
                ap += relevant_found / rank

        ap = ap / len(relevant_docs) if relevant_docs else 0

        return {
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'average_precision': ap
        }

    def evaluate_all_methods(self, top_k: int = 10) -> Dict[str, Dict[str, float]]:
        """
        Evaluate all retrieval methods
        Returns: Dictionary with average metrics for each method
        """
        print("Creating test queries...")
        test_queries = self.create_test_queries()
        print(f"Evaluating on {len(test_queries)} test queries...\n")

        methods = ['boolean', 'vsm', 'bm25']
        results = {method: defaultdict(list) for method in methods}

        for query, relevant_docs in test_queries:
            print(f"Evaluating query: '{query}'")

            for method in methods:
                metrics = self.evaluate(query, relevant_docs, method, top_k)

                for metric_name, value in metrics.items():
                    results[method][metric_name].append(value)

                print(f"  {method.upper()}: P={metrics['precision']:.3f}, "
                      f"R={metrics['recall']:.3f}, F1={metrics['f1']:.3f}, "
                      f"AP={metrics['average_precision']:.3f}")
            print()

        # Calculate averages
        avg_results = {}
        for method in methods:
            avg_results[method] = {
                metric: np.mean(values)
                for metric, values in results[method].items()
            }

        return avg_results

    @staticmethod
    def print_evaluation_results(results: Dict[str, Dict[str, float]]):
        """Print evaluation results in a formatted table"""
        print(f"\n{'='*80}")
        print("EVALUATION RESULTS - Average Metrics")
        print(f"{'='*80}\n")

        print(f"{'Method':<15} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'Avg Precision':<15}")
        print(f"{'-'*80}")

        for method, metrics in results.items():
            print(f"{method.upper():<15} "
                  f"{metrics['precision']:<12.4f} "
                  f"{metrics['recall']:<12.4f} "
                  f"{metrics['f1']:<12.4f} "
                  f"{metrics['average_precision']:<15.4f}")

        print(f"{'='*80}\n")

def main():
    """Main function with CLI interface"""
    print("Reuters Search Engine")
    print("=" * 80)

    # Initialize and build index
    engine = SearchEngine()
    engine.build_index(sample_size=1000)  # Use 1000 docs for demo

    print("\n" + "=" * 80)
    print("Search Engine Ready!")
    print("=" * 80)

    while True:
        print("\nOptions:")
        print("1. Search")
        print("2. Evaluate all methods")
        print("3. Exit")

        choice = input("\nEnter your choice (1-3): ").strip()

        if choice == '1':
            # Get search parameters
            query = input("\nEnter your search query: ").strip()

            if not query:
                print("Empty query. Please try again.")
                continue

            print("\nSelect retrieval method:")
            print("1. Boolean (AND/OR/NOT)")
            print("2. Vector Space Model (TF-IDF)")
            print("3. BM25")

            method_choice = input("Enter method (1-3): ").strip()

            method_map = {'1': 'boolean', '2': 'vsm', '3': 'bm25'}
            method = method_map.get(method_choice, 'bm25')

            boolean_op = 'AND'
            if method == 'boolean':
                print("\nSelect boolean operator:")
                print("1. AND (all terms must match)")
                print("2. OR (any term must match)")
                print("3. NOT (exclude documents with terms)")
                op_choice = input("Enter operator (1-3): ").strip()
                op_map = {'1': 'AND', '2': 'OR', '3': 'NOT'}
                boolean_op = op_map.get(op_choice, 'AND')

            top_k = 10
            if method != 'boolean':
                top_k_input = input("\nNumber of results to show (default 10): ").strip()
                if top_k_input.isdigit():
                    top_k = int(top_k_input)

            # Perform search
            results = engine.search(query, method=method, top_k=top_k,
                                    boolean_op=boolean_op)

            # Display results
            engine.display_results(results, query, method)

        elif choice == '2':
            # Evaluate all methods
            evaluator = SearchEvaluator(engine)
            results = evaluator.evaluate_all_methods(top_k=10)
            evaluator.print_evaluation_results(results)

        elif choice == '3':
            print("\nThank you for using Reuters Search Engine!")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()