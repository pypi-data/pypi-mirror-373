"""
bm25s API Compatibility Layer

This module provides a drop-in replacement for the bm25s library,
making migration seamless while providing better performance.
"""

import bm25
from typing import List, Union, Optional, Tuple


def tokenize(text: Union[str, List[str]], language: str = "en", compound_words: Optional[List[str]] = None, stopwords: Optional[List[str]] = None) -> Union[List[str], List[List[str]]]:
    """
    Tokenize text using SmartTokenizer (similar to bm25s.tokenize())
    
    This function provides the same interface as bm25s.tokenize() but uses
    the intelligent SmartTokenizer for better tokenization quality.
    
    Args:
        text: Text to tokenize (string) or list of texts to tokenize
        language: Language code for tokenization (default: "en" for English)
        compound_words: Optional list of compound words to preserve
        stopwords: Optional list of stopwords to filter out (default: None)
    
    Returns:
        If text is a string: List of tokens
        If text is a list: List of lists of tokens
        
    Example:
        >>> tokens = tokenize("Hello world! This is a test.")
        >>> print(tokens)
        ['hello', 'world', 'this', 'is', 'a', 'test']
        
        >>> docs = ["Hello world!", "This is a test."]
        >>> all_tokens = tokenize(docs)
        >>> print(all_tokens)
        [['hello', 'world'], ['this', 'is', 'a', 'test']]
    """
    # Handle single text vs list of texts
    if isinstance(text, str):
        single_text = True
        texts = [text]
    else:
        single_text = False
        texts = text
    
    # Create appropriate tokenizer based on parameters
    if compound_words:
        if language == "en":
            tokenizer = bm25.NewEnglishSmartTokenizerWithCompounds(compound_words)
        else:
            tokenizer = bm25.NewSmartTokenizerWithCompounds(language, compound_words)
    else:
        if language == "en":
            tokenizer = bm25.NewEnglishSmartTokenizer()
        else:
            tokenizer = bm25.NewSmartTokenizer(language)
    
    # Tokenize all texts
    all_tokens = []
    for text_item in texts:
        tokens = tokenizer.Tokenize(text_item)
        token_list = list(tokens)
        
        # Filter out stopwords if provided
        if stopwords:
            token_list = [token for token in token_list if token.lower() not in [sw.lower() for sw in stopwords]]
        
        all_tokens.append(token_list)
    
    # Return single list for single text, list of lists for multiple texts
    if single_text:
        return all_tokens[0]
    else:
        return all_tokens


class BM25:
    """
    Drop-in replacement for bm25s.BM25()
    
    This class provides the exact same API as bm25s.BM25() but with
    the performance benefits of the Go-based implementation.
    """
    
    def __init__(self, documents: Optional[List[List[str]]] = None, 
                 k1: float = 1.2, b: float = 0.75, 
                 epsilon: float = 0.25,
                 tokenizer_name: Optional[str] = None):
        """
        Initialize BM25 index
        
        Args:
            documents: List of tokenized documents (optional)
            k1: BM25 parameter k1 (default: 1.2)
            b: BM25 parameter b (default: 0.75)
            epsilon: BM25 parameter epsilon (default: 0.25)
            tokenizer_name: Tokenizer to use - "simple" for DefaultTokenizer, 
                           "en" for English SmartTokenizer, or None for English SmartTokenizer (default: None)
        
        Note: k1, b, and epsilon parameters are stored but not yet implemented
              in the underlying Go implementation. They're kept for API compatibility.
        """
        self.k1 = k1
        self.b = b
        self.epsilon = epsilon
        
        # Estimate capacities based on input documents
        if documents:
            doc_capacity = len(documents)
            term_capacity = max(len(set(term for doc in documents for term in doc)), 1000)
        else:
            doc_capacity = 1000
            term_capacity = 10000
        
        # Create underlying Go index
        self._index = bm25.new_bm25_index(doc_capacity, term_capacity)
        
        # Set tokenizer based on tokenizer_name parameter
        if tokenizer_name == "simple":
            self._tokenizer = bm25.DefaultTokenizer()
        else:
            # Default to English SmartTokenizer (for None or "en")
            self._tokenizer = bm25.new_english_smart_tokenizer()
        
        self._documents = []
        self._doc_ids = []
        
        # Add documents if provided
        if documents:
            self.index(documents)
    
    def tokenize(self, text: Union[str, List[str]], language: str = "en", compound_words: Optional[List[str]] = None, stopwords: Optional[List[str]] = None) -> Union[List[str], List[List[str]]]:
        """
        Tokenize text using SmartTokenizer (similar to bm25s.tokenize())
        
        This method provides the same interface as bm25s.tokenize() but uses
        the intelligent SmartTokenizer for better tokenization quality.
        
        Args:
            text: Text to tokenize (string) or list of texts to tokenize
            language: Language code for tokenization (default: "en" for English)
            compound_words: Optional list of compound words to preserve
            stopwords: Optional list of stopwords to filter out (default: None)
        
        Returns:
            If text is a string: List of tokens
            If text is a list: List of lists of tokens
            
        Example:
            >>> bm25_index = BM25()
            >>> tokens = bm25_index.tokenize("Hello world! This is a test.")
            >>> print(tokens)
            ['hello', 'world', 'this', 'is', 'a', 'test']
            
            >>> docs = ["Hello world!", "This is a test."]
            >>> all_tokens = bm25_index.tokenize(docs)
            >>> print(all_tokens)
            [['hello', 'world'], ['this', 'is', 'a', 'test']]
        """
        return tokenize(text, language, compound_words, stopwords)
    
    def index(self, documents: List[List[str]]):
        """
        Index a list of tokenized documents
        
        Args:
            documents: List of tokenized documents (list of lists of strings)
        """
        self._documents = documents
        self._doc_ids = []
        
        # Clear existing index
        self._index.clear()
        
        # Add each document
        for i, doc_tokens in enumerate(documents):
            doc_id = f"doc_{i}"
            self._doc_ids.append(doc_id)
            
            # Join tokens back into text for our implementation
            doc_text = " ".join(doc_tokens)
            self._index.add_document(doc_id, doc_text)
    
    def retrieve(self, query: Union[List[str], List[List[str]]], k: int = 10, 
                 sorted: bool = True, return_as: str = "tuple") -> Union[List[int], Tuple[List[int], List[float]], List[List[int]], List[Tuple[List[int], List[float]]]]:
        """
        Retrieve top-k documents for a query
        
        Args:
            query: Query tokens (list of strings) or list of query tokens
            k: Number of top results to return (default: 10)
            sorted: If True, returns documents in sorted order (default: True)
            return_as: Return format - "tuple" returns (documents, scores), 
                      "documents" returns only documents (default: "tuple")
        
        Returns:
            For single query:
                If return_as="tuple": tuple of (document_indices, scores)
                If return_as="documents": list of document indices (0-based) in relevance order
            For batch queries:
                If return_as="tuple": list of tuples (document_indices, scores)
                If return_as="documents": list of lists of document indices
        """
        # Handle both single query and list of queries
        if isinstance(query[0], list):
            # List of queries - this is batch search
            return self._batch_retrieve(query, k, sorted, return_as)
        else:
            # Single query
            return self._single_retrieve(query, k, sorted, return_as)
    
    def _single_retrieve(self, query_tokens: List[str], k: int = 10, 
                         sorted: bool = True, return_as: str = "tuple") -> Union[List[int], Tuple[List[int], List[float]]]:
        """Handle single query retrieval."""
        # Join tokens into text for our search
        query_text = " ".join(query_tokens)
        
        # Search using our implementation
        results = self._index.search(query_text, k)
        
        # Convert results to document indices and scores
        doc_indices = []
        scores = []
        for result in results:
            # Extract index from doc_id (e.g., "doc_5" -> 5)
            try:
                doc_index = int(result['DocID'].split("_")[1])
                doc_indices.append(doc_index)
                scores.append(result['Score'])
            except (ValueError, IndexError):
                # Fallback: try to find by doc_id in our list
                try:
                    doc_index = self._doc_ids.index(result['DocID'])
                    doc_indices.append(doc_index)
                    scores.append(result['Score'])
                except ValueError:
                    continue
        
        # Return based on return_as parameter
        if return_as == "documents":
            return doc_indices
        else: # default to "tuple"
            return (doc_indices, scores)
    
    def _batch_retrieve(self, queries: List[List[str]], k: int = 10, 
                        sorted: bool = True, return_as: str = "tuple") -> Union[List[List[int]], List[Tuple[List[int], List[float]]]]:
        """Handle batch query retrieval efficiently using BatchSearch."""
        # Convert token lists to query strings
        query_strings = [" ".join(query_tokens) for query_tokens in queries]
        
        # Use the efficient batch search
        batch_results = self._index.batch_search(query_strings, self._tokenizer, k)
        
        # Process results
        if return_as == "documents":
            # Return list of lists of document indices
            all_doc_indices = []
            for batch_result in batch_results:
                doc_indices = []
                for result in batch_result.results:
                    try:
                        doc_index = int(result['DocID'].split("_")[1])
                        doc_indices.append(doc_index)
                    except (ValueError, IndexError):
                        # Fallback: try to find by doc_id in our list
                        try:
                            doc_index = self._doc_ids.index(result['DocID'])
                            doc_indices.append(doc_index)
                        except ValueError:
                            continue
                all_doc_indices.append(doc_indices)
            return all_doc_indices
        else:
            # Return list of tuples (document_indices, scores)
            all_results = []
            for batch_result in batch_results:
                doc_indices = []
                scores = []
                for result in batch_result.results:
                    try:
                        doc_index = int(result['DocID'].split("_")[1])
                        doc_indices.append(doc_index)
                        scores.append(result['Score'])
                    except (ValueError, IndexError):
                        # Fallback: try to find by doc_id in our list
                        try:
                            doc_index = self._doc_ids.index(result['DocID'])
                            doc_indices.append(doc_index)
                            scores.append(result['Score'])
                        except ValueError:
                            continue
                all_results.append((doc_indices, scores))
            return all_results
    
    def get_scores(self, query: List[str]) -> List[float]:
        """
        Get BM25 scores for all documents for a query
        
        Args:
            query: Query tokens (list of strings)
        
        Returns:
            List of BM25 scores for all documents
        """
        query_text = " ".join(query)
        results = self._index.Search(query_text, self._tokenizer, len(self._documents))
        
        # Create a mapping of doc_id to score
        scores_map = {result.DocID: result.Score for result in results}
        
        # Return scores in document order
        scores = []
        for doc_id in self._doc_ids:
            scores.append(scores_map.get(doc_id, 0.0))
        
        return scores
    
    def get_top_n(self, query: List[str], n: int = 10) -> List[int]:
        """
        Get top-n document indices for a query
        
        Args:
            query: Query tokens (list of strings)
            n: Number of top results to return (default: 10)
        
        Returns:
            List of document indices (0-based) in relevance order
        """
        return self.retrieve(query, n)
    
    def batch_retrieve(self, queries: List[List[str]], k: int = 10, 
                       sorted: bool = True, return_as: str = "tuple") -> Union[List[List[int]], List[Tuple[List[int], List[float]]]]:
        """
        Efficiently retrieve top-k documents for multiple queries using batch search
        
        Args:
            queries: List of query token lists (list of lists of strings)
            k: Number of top results to return per query (default: 10)
            sorted: If True, returns documents in sorted order (default: True)
            return_as: Return format - "tuple" returns list of (documents, scores) tuples,
                      "documents" returns list of lists of document indices (default: "tuple")
        
        Returns:
            If return_as="tuple": list of tuples (document_indices, scores) for each query
            If return_as="documents": list of lists of document indices for each query
        
        Example:
            >>> queries = [["machine", "learning"], ["artificial", "intelligence"]]
            >>> results = bm25_index.batch_retrieve(queries, k=5)
            >>> # Returns: [([0, 2, 5], [0.8, 0.6, 0.4]), ([1, 3, 4], [0.9, 0.7, 0.5])]
        """
        return self._batch_retrieve(queries, k, sorted, return_as)
    
    def get_document_count(self) -> int:
        """
        Get the total number of documents in the index
        
        Returns:
            Number of documents
        """
        return self._index.get_document_count()
    
    def get_term_count(self) -> int:
        """
        Get the total number of unique terms in the index
        
        Returns:
            Number of documents
        """
        return self._index.get_term_count()
    
    def get_avgdl(self) -> float:
        """
        Get the average document length
        
        Returns:
            Average document length
        """
        return self._index.get_average_document_length()
    
    def get_corpus_size(self) -> int:
        """
        Get the total corpus size (same as document count)
        
        Returns:
            Number of documents
        """
        return self.get_document_count()
    
    def get_document(self, doc_index: int) -> List[str]:
        """
        Get a document by index
        
        Args:
            doc_index: Document index (0-based)
        
        Returns:
            List of tokens in the document
        
        Raises:
            IndexError: If doc_index is out of range
        """
        if doc_index < 0 or doc_index >= len(self._documents):
            raise IndexError(f"Document index {doc_index} out of range")
        return self._documents[doc_index]
    
    def get_documents(self) -> List[List[str]]:
        """
        Get all documents in the index
        
        Returns:
            List of all tokenized documents
        """
        return self._documents.copy()
    
    def add_document(self, document: List[str]):
        """
        Add a single document to the index
        
        Args:
            document: Tokenized document (list of strings)
        """
        doc_id = f"doc_{len(self._documents)}"
        self._documents.append(document)
        self._doc_ids.append(doc_id)
        
        # Join tokens into text for our implementation
        doc_text = " ".join(document)
        self._index.AddDocument(doc_id, doc_text, self._tokenizer)
    
    def clear(self):
        """
        Clear all documents from the index
        """
        self._index.Clear()
        self._documents.clear()
        self._doc_ids.clear()
    
    def __len__(self) -> int:
        """
        Get the number of documents in the index
        """
        return len(self._documents)


# Convenience function for easy migration
def create_bm25(documents: Optional[List[List[str]]] = None, 
                k1: float = 1.2, b: float = 0.75, 
                epsilon: float = 0.25,
                tokenizer_name: Optional[str] = None) -> BM25:
    """
    Create a BM25 index (alias for BM25 constructor)
    
    This function provides the same interface as bm25s.create_bm25()
    
    Args:
        documents: List of tokenized documents (optional)
        k1: BM25 parameter k1 (default: 1.2)
        b: BM25 parameter b (default: 0.75)
        epsilon: BM25 parameter epsilon (default: 0.25)
        tokenizer_name: Tokenizer to use - "simple" for DefaultTokenizer, 
                       "en" for English SmartTokenizer, or None for English SmartTokenizer (default: None)
    
    Returns:
        BM25 index instance
    """
    return BM25(documents, k1, b, epsilon, tokenizer_name)


# Export the main class and functions for easy import
__all__ = ['BM25', 'create_bm25', 'tokenize'] 