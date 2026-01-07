from nltk.corpus import reuters
from typing import List, Tuple, Set, Dict
from collections import defaultdict
from textwrap import dedent
import numpy
import os

from search_engine.downloader import download_datasets
from search_engine.text_processor import TextProcessor
from search_engine.inverted_index import InvertedIndex
from search_engine.boolean_retrieval import BooleanRetrieval
from search_engine.vector_space_model import VectorSpaceModel
from search_engine.okapi_bm25 import OkapiBM25


class SearchEngine:
    def __init__(self):
        self.processor = TextProcessor()
        self.inverted_index = InvertedIndex()
        self.boolean_retrieval = None
        self.vsm = None
        self.bm25 = None
        self.raw_documents = {}
        self.processed_documents = {}

    def build_index_from_reuters(self, sample_size: int = 1000):
        """Build index from Reuters corpus"""
        print(f"Loading Reuters corpus with a sample size of {sample_size}...")
        file_ids = reuters.fileids()[:sample_size]

        for file_id in file_ids:
            # Get raw text
            raw_text = reuters.raw(file_id)
            self.raw_documents[file_id] = raw_text

            # Process text
            processed = self.processor.process(raw_text)
            self.processed_documents[file_id] = processed

        self.inverted_index.build(self.processed_documents)

        # Initialize retrieval models
        self.boolean_retrieval = BooleanRetrieval(self.inverted_index)
        self.vsm = VectorSpaceModel(self.inverted_index)
        self.bm25 = OkapiBM25(self.inverted_index)

        print(dedent(f"""
        Index built successfully from Reuters corpus.
        Total documents: {self.inverted_index.total_docs}
        Vocabulary size: {len(self.inverted_index.index)}
        Average document length: {self.inverted_index.avg_doc_length:.2f} terms"""))

    def build_index_from_cisi(self, cisi_path: str):
        """Build index from CISI"""
        print(f"Loading CISI...")

        # Parse CISI documents
        docs = self.parse_cisi_documents(os.path.join(cisi_path, 'CISI.ALL'))

        for doc_id, raw_text in docs.items():
            self.raw_documents[doc_id] = raw_text
            processed = self.processor.process(raw_text)
            self.processed_documents[doc_id] = processed

        self.inverted_index.build(self.processed_documents)

        # Initialize retrieval models
        self.boolean_retrieval = BooleanRetrieval(self.inverted_index)
        self.vsm = VectorSpaceModel(self.inverted_index)
        self.bm25 = OkapiBM25(self.inverted_index)

        print(dedent(f"""
        Index built successfully from CISI.
        Total documents: {self.inverted_index.total_docs}
        Vocabulary size: {len(self.inverted_index.index)}
        Average document length: {self.inverted_index.avg_doc_length:.2f} terms
        """))

    @staticmethod
    def parse_cisi_documents(filepath: str) -> Dict[str, str]:
        """Parse CISI.ALL file and extract documents"""
        documents = {}
        current_doc_id = None
        current_field = None
        current_content = []

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.rstrip()

                if line.startswith('.I'):
                    # Save previous document
                    if current_doc_id and current_content:
                        documents[current_doc_id] = ' '.join(current_content)

                    # Start new document
                    current_doc_id = f"CISI_{line.split()[1]}"
                    current_content = []
                    current_field = None

                elif line.startswith('.T') or line.startswith('.W') or line.startswith('.A'):
                    # These are the main content fields (Title, Abstract/Words, Author)
                    current_field = line[1]

                elif line.startswith('.'):
                    # Other fields we don't include in the document text
                    current_field = None

                elif current_field in ['T', 'W', 'A'] and line.strip():
                    current_content.append(line.strip())

            # Save last document
            if current_doc_id and current_content:
                documents[current_doc_id] = ' '.join(current_content)

        return documents

    def search(self, query: str, method: str = 'bm25', top_n: int = 10,
               boolean_op: str = 'AND') -> List[Tuple[str, float]]:
        """
        Search for documents matching the query.

        Args:
            query (str): Search query string.
            method (str, optional): 'boolean', 'vsm', 'bm25'. Defaults to 'bm25'.
            boolean_op (str, optional): 'AND', 'OR', 'NOT'. Defaults to 'AND'.
            top_n (int): Top n results to return. Defaults to 10.

        Returns:
            List of (doc_id, score) tuples.
        """

        # Process query
        query_terms = self.processor.process(query)

        if not query_terms:
            return []

        # Search using the user-specified method
        match method:
            case 'boolean':
                doc_ids = self.boolean_retrieval.search(query_terms, boolean_op)
                # Boolean does not rank, assign a score of 1.0
                return [(doc_id, 1.0) for doc_id in doc_ids[:top_n]]
            case 'vsm':
                return self.vsm.search(query_terms, top_n)
            case 'bm25':
                return self.bm25.search(query_terms, top_n)
            case _:
                raise ValueError(f"Unknown method '{method}'")

    def display_results(self, results: List[Tuple[str, float]], query: str,
                        method: str, max_length: int = 200):
        """Display search results in a user-friendly format"""
        print(dedent(f"""
        {'=' * 80}
        Query: '{query}'
        Method: '{method}'
        Found {len(results)} documents
        {'=' * 80}"""))

        for rank, (doc_id, score) in enumerate(results, 1):
            raw_text = self.raw_documents.get(doc_id, "")

            # Truncate for display
            preview = raw_text[:max_length].replace('\n', ' ')
            if len(raw_text) > max_length:
                preview += "..."

            print(dedent(f"""
            \x1B[32m{rank}. {doc_id}\x1B[0m
            Score: {score:.4f}
            Preview: {preview}
            Categories: {', '.join(reuters.categories(doc_id))}
            """))


class SearchEvaluator:
    """Evaluate search engine performance"""

    def __init__(self, search_engine: SearchEngine):
        self.search_engine = search_engine

    @staticmethod
    def create_reuters_test_queries() -> List[Tuple[str, Set[str]]]:
        """
        Create test queries with relevance judgments.

        Returns:
            List of (doc_id, relevant_doc_ids) tuples.
        """

        test_queries = []

        # Sample some categories
        categories = ['acq', 'earn', 'crude', 'trade', 'money-fx']

        for category in categories:
            # Get documents in this category
            relevant_docs = set(reuters.fileids(category)[:100])

            if relevant_docs:
                # Create query based on category name
                test_queries.append((category, relevant_docs))

        return test_queries

    def create_cisi_test_queries(self, cisi_path: str) -> List[Tuple[str, Set[str]]]:
        """
        Create test queries with relevance judgments for CISI.

        Returns:
            List of (query, relevant_doc_ids) tuples.
        """
        queries = self.parse_cisi_queries(os.path.join(cisi_path, 'CISI.QRY'))
        relevance = self.parse_cisi_relevance(os.path.join(cisi_path, 'CISI.REL'))

        test_queries = []
        for query_id, query_text in queries.items():
            if query_id in relevance:
                relevant_docs = {f"CISI_{doc_id}" for doc_id in relevance[query_id]}
                test_queries.append((query_text, relevant_docs))

        return test_queries[:5]

    @staticmethod
    def parse_cisi_queries(filepath: str) -> Dict[str, str]:
        """Parse CISI.QRY file and extract queries"""
        queries = {}
        current_query_id = None
        current_field = None
        current_content = []

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.rstrip()

                if line.startswith('.I'):
                    # Save previous query
                    if current_query_id and current_content:
                        queries[current_query_id] = ' '.join(current_content)

                    # Start new query
                    current_query_id = line.split()[1]
                    current_content = []
                    current_field = None

                elif line.startswith('.W'):
                    # Query text field
                    current_field = 'W'

                elif line.startswith('.'):
                    current_field = None

                elif current_field == 'W' and line.strip():
                    current_content.append(line.strip())

            # Save last query
            if current_query_id and current_content:
                queries[current_query_id] = ' '.join(current_content)

        return queries

    @staticmethod
    def parse_cisi_relevance(filepath: str) -> Dict[str, Set[str]]:
        """Parse CISI.REL file and extract relevance judgments"""
        relevance = defaultdict(set)

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    query_id = parts[0]
                    doc_id = parts[1]
                    relevance[query_id].add(doc_id)

        return relevance

    def evaluate(self, query: str, relevant_docs: Set[str], method: str,
                 top_n: int = 10) -> Dict[str, float]:
        """
        Evaluate a single query.

        Returns:
            Dictionary with precision, recall, F1, and AP.
        """

        # Get search results
        results = self.search_engine.search(query, method=method, top_n=top_n)
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

    def evaluate_all_methods_reuters(self, top_n: int = 10) -> Dict[str, Dict[str, float]]:
        """
        Evaluate all retrieval methods.

        Returns:
            Dictionary with average metrics for each method.
        """

        test_queries = self.create_reuters_test_queries()

        methods = ['boolean', 'vsm', 'bm25']
        results = {method: defaultdict(list) for method in methods}

        for query, relevant_docs in test_queries:
            print(f"\x1B[3mEvaluating query: '{query}'\x1B[0m")

            for method in methods:
                metrics = self.evaluate(query, relevant_docs, method, top_n)

                for metric_name, value in metrics.items():
                    results[method][metric_name].append(value)

                print(dedent(f"""
                {method.upper()}: P={metrics['precision']:.3f},
                R={metrics['recall']:.3f}, F1={metrics['f1']:.3f},
                AP={metrics['average_precision']:.3f}
                """))
            print()

        # Calculate averages
        avg_results = {}
        for method in methods:
            avg_results[method] = {
                metric: numpy.mean(values)
                for metric, values in results[method].items()
            }

        return avg_results

    def evaluate_all_methods_cisi(self, cisi_path: str, top_n: int = 10) -> Dict[str, Dict[str, float]]:
        """
        Evaluate all retrieval methods on CISI dataset.

        Returns:
            Dictionary with average metrics for each method.
        """

        test_queries = self.create_cisi_test_queries(cisi_path)

        methods = ['boolean', 'vsm', 'bm25']
        results = {method: defaultdict(list) for method in methods}

        for query, relevant_docs in test_queries:
            print(f"\x1B[3mEvaluating query: '{query[:50]}...'\x1B[0m")

            for method in methods:
                metrics = self.evaluate(query, relevant_docs, method, top_n)

                for metric_name, value in metrics.items():
                    results[method][metric_name].append(value)

                print(dedent(f"""
                {method.upper()}: P={metrics['precision']:.3f},
                R={metrics['recall']:.3f}, F1={metrics['f1']:.3f},
                AP={metrics['average_precision']:.3f}
                """))
            print()

        # Calculate averages
        avg_results = {}
        for method in methods:
            avg_results[method] = {
                metric: numpy.mean(values)
                for metric, values in results[method].items()
            }

        return avg_results

    @staticmethod
    def print_evaluation_results(results: Dict[str, Dict[str, float]], dataset_name: str):
        """Print evaluation results in a formatted table with dataset name"""
        print(dedent(f"""
        {'=' * 80}
        Evaluation Results - {dataset_name}
        {'=' * 80}
        {'Method':<15} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'Avg. Precision':<16}
        {'-' * 80}
        """))

        for method, metrics in results.items():
            print(f"{method.upper():<15} "
                  f"{metrics['precision']:<12.4f} "
                  f"{metrics['recall']:<12.4f} "
                  f"{metrics['f1']:<12.4f} "
                  f"{metrics['average_precision']:<15.4f}")

        print(f"{'=' * 80}\n")


def main():
    cisi_path = download_datasets()
    engine = SearchEngine()
    engine.build_index_from_reuters()

    while True:
        print(dedent("""
        -- Options --
        1. Search
        2. Evaluate all methods
        3. Exit"""))

        choice = input(">> ").strip()

        match choice:
            case '1':
                query = input("Enter your search query: ").strip()
                if not query:
                    print("Empty query, please try again")
                    continue

                print(dedent(f"""
                -- Select retrieval method --
                1. Boolean
                2. Vector Space Model (TF-IDF)
                3. BM25"""))
                method_choice = input(">> ").strip()

                method_map = {'1': 'boolean', '2': 'vsm', '3': 'bm25'}
                method = method_map.get(method_choice, 'bm25')

                boolean_op = 'AND'
                if method == 'boolean':
                    print(dedent("""
                    -- Select boolean operator --
                    1. AND (all terms must match)
                    2. OR (any terms must match)
                    3. NOT (exclude documents containing the given terms)"""))
                    op_choice = input(">> ").strip()
                    op_map = {'1': 'AND', '2': 'OR', '3': 'NOT'}
                    boolean_op = op_map.get(op_choice, 'AND')

                top_n = 10
                if method != 'boolean':
                    top_n_input = input("\n# of results to show (default: 10) ").strip()
                    if top_n_input.isdigit():
                        top_n = int(top_n_input)

                # Perform search
                results = engine.search(query, method=method, top_n=top_n, boolean_op=boolean_op)

                # Display results
                engine.display_results(results, query, method)

            case '2':
                # Evaluate all methods on both datasets
                print(dedent(f"""
                {'=' * 80}
                Evaluating Reuters dataset...
                {'=' * 80}
                """))

                evaluator = SearchEvaluator(engine)
                reuters_results = evaluator.evaluate_all_methods_reuters(top_n=10)

                print(dedent(f"""
                {'=' * 80}
                Evaluating CISI dataset...
                {'=' * 80}
                """))

                cisi_engine = SearchEngine()
                cisi_engine.build_index_from_cisi(cisi_path)
                cisi_evaluator = SearchEvaluator(cisi_engine)
                cisi_results = cisi_evaluator.evaluate_all_methods_cisi(cisi_path, top_n=10)

                evaluator.print_evaluation_results(reuters_results, "Reuters")
                cisi_evaluator.print_evaluation_results(cisi_results, "CISI")

            case '3':
                print("Exiting, bye...")
                break

            case _:
                print("Invalid choice, please try again")


if __name__ == "__main__":
    main()
