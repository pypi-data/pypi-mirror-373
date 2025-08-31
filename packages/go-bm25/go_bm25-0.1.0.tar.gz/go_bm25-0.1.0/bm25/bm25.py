"""
Python wrapper for Go BM25 library using ctypes.

This module provides Python bindings for the high-performance BM25 ranking
algorithm implementation written in Go.
"""

import ctypes
import json
import os
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

# Load the shared library
def _load_library():
    """Load the Go shared library."""
    # Get the directory where this Python file is located
    current_dir = Path(__file__).parent
    
    # Try to find the shared library
    lib_paths = [
        current_dir / "libbm25.so",      # Linux
        current_dir / "libbm25.dylib",   # macOS
        current_dir / "libbm25.dll",     # Windows
    ]
    
    for lib_path in lib_paths:
        if lib_path.exists():
            return ctypes.CDLL(str(lib_path))
    
    raise FileNotFoundError(f"Could not find BM25 shared library in {current_dir}")

try:
    _lib = _load_library()
except Exception as e:
    print(f"Warning: Could not load BM25 library: {e}")
    _lib = None

# Define function signatures
if _lib:
    _lib.HelloBM25.restype = ctypes.c_char_p
    _lib.NewBM25Index.argtypes = [ctypes.c_int, ctypes.c_int]
    _lib.NewBM25Index.restype = ctypes.c_longlong
    _lib.AddDocument.argtypes = [ctypes.c_longlong, ctypes.c_char_p, ctypes.c_char_p]
    _lib.AddDocument.restype = ctypes.c_int
    _lib.Search.argtypes = [ctypes.c_longlong, ctypes.c_char_p, ctypes.c_int]
    _lib.Search.restype = ctypes.c_char_p
    _lib.CreateEnglishSmartTokenizer.restype = ctypes.c_longlong
    _lib.CreateSmartTokenizer.argtypes = [ctypes.c_char_p]
    _lib.CreateSmartTokenizer.restype = ctypes.c_longlong
    _lib.TokenizeText.argtypes = [ctypes.c_longlong, ctypes.c_char_p]
    _lib.TokenizeText.restype = ctypes.c_char_p
    
    # Batch search functions
    _lib.BatchSearch.argtypes = [ctypes.c_longlong, ctypes.c_char_p, ctypes.c_longlong, ctypes.c_int]
    _lib.BatchSearch.restype = ctypes.c_char_p
    
    # GetMatches function
    _lib.GetMatches.argtypes = [ctypes.c_longlong, ctypes.c_char_p, ctypes.c_char_p]
    _lib.GetMatches.restype = ctypes.c_char_p

class TermMatch:
    """Represents a term match found in a document."""
    
    def __init__(self, term: str, frequency: int, position: int):
        """
        Initialize a term match.
        
        Args:
            term: The term that was matched
            frequency: Frequency of the term in the document
            position: Position of the term in the document
        """
        self._term = term
        self._frequency = frequency
        self._position = position
    
    @property
    def term(self) -> str:
        """Get the matched term."""
        return self._term
    
    @property
    def frequency(self) -> int:
        """Get the frequency of the term in the document."""
        return self._frequency
    
    @property
    def position(self) -> int:
        """Get the position of the term in the document."""
        return self._position
    
    def __repr__(self) -> str:
        return f"TermMatch(term='{self._term}', frequency={self._frequency}, position={self._position})"

class BatchSearchResult:
    """Result from a batch search operation."""
    
    def __init__(self, query: str, results: List[Dict[str, Any]]):
        """
        Initialize a batch search result.
        
        Args:
            query: The query that was searched
            results: List of search results
        """
        self._query = query
        self._results = results
    
    @property
    def query(self) -> str:
        """Get the query that was searched."""
        return self._query
    
    @property
    def results(self) -> List[Dict[str, Any]]:
        """Get the search results for this query."""
        return self._results


class BM25Index:
    """BM25 index for document ranking."""
    
    def __init__(self, doc_capacity: int = 1000, term_capacity: int = 10000):
        """
        Initialize a new BM25 index.
        
        Args:
            doc_capacity: Initial capacity for documents
            term_capacity: Initial capacity for terms
        """
        if not _lib:
            raise RuntimeError("BM25 library not available")
        
        self.handle = _lib.NewBM25Index(ctypes.c_int(doc_capacity), ctypes.c_int(term_capacity))
        if self.handle == 0:
            raise RuntimeError("Failed to create BM25 index")
    
    def add_document(self, doc_id: str, content: str) -> bool:
        """
        Add a document to the index.
        
        Args:
            doc_id: Unique document identifier
            content: Document text content
            
        Returns:
            True if document was added successfully, False otherwise
        """
        if not _lib:
            raise RuntimeError("BM25 library not available")
        
        result = _lib.AddDocument(
            self.handle,
            doc_id.encode('utf-8'),
            content.encode('utf-8')
        )
        return result == 0
    
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for documents matching the query.
        
        Args:
            query: Search query text
            limit: Maximum number of results to return
            
        Returns:
            List of search results with document IDs and scores
        """
        if not _lib:
            raise RuntimeError("BM25 library not available")
        
        result_ptr = _lib.Search(self.handle, query.encode('utf-8'), ctypes.c_int(limit))
        if result_ptr:
            result_json = ctypes.string_at(result_ptr).decode('utf-8')
            try:
                return json.loads(result_json)
            except json.JSONDecodeError:
                return []
        return []
    
    def clear(self):
        """Clear all documents from the index."""
        if not _lib:
            raise RuntimeError("BM25 library not available")
        
        # Note: Clear method is not currently exposed in the Python bindings
        # We'll implement a workaround by creating a new index
        self.handle = _lib.NewBM25Index(ctypes.c_int(1000), ctypes.c_int(10000))
        if self.handle == 0:
            raise RuntimeError("Failed to create new BM25 index")
    
    def batch_search(self, queries: List[str], tokenizer, limit: int = 10) -> List[BatchSearchResult]:
        """
        Perform batch search for multiple queries efficiently.
        
        Args:
            queries: List of search query strings
            tokenizer: Tokenizer to use for queries
            limit: Maximum number of results per query
            
        Returns:
            List of BatchSearchResult objects
        """
        if not _lib:
            raise RuntimeError("BM25 library not available")
        
        # Get tokenizer handle (assuming it has a handle attribute)
        tokenizer_handle = getattr(tokenizer, 'handle', 0)
        
        # Convert queries to JSON string
        queries_json = json.dumps(queries)
        
        # Call the batch search function
        results_ptr = _lib.BatchSearch(
            ctypes.c_longlong(self.handle),
            queries_json.encode('utf-8'),
            ctypes.c_longlong(tokenizer_handle),
            ctypes.c_int(limit)
        )
        
        if not results_ptr:
            return []
        
        # Parse the results JSON
        try:
            results_json = ctypes.string_at(results_ptr).decode('utf-8')
            batch_results_data = json.loads(results_json)
            
            # Convert to BatchSearchResult objects
            batch_results = []
            for result_data in batch_results_data:
                query = result_data.get('Query', '')
                results = result_data.get('Results', [])
                batch_results.append(BatchSearchResult(query, results))
            
            return batch_results
        except (json.JSONDecodeError, AttributeError):
            return []
    
    def get_document_count(self) -> int:
        """Get the total number of documents in the index."""
        # Note: This is a placeholder since the actual method isn't exposed
        # In a real implementation, this would call the Go library
        return 0
    
    def get_term_count(self) -> int:
        """Get the total number of unique terms in the index."""
        # Note: This is a placeholder since the actual method isn't exposed
        # In a real implementation, this would call the Go library
        return 0
    
    def get_average_document_length(self) -> float:
        """Get the average document length."""
        # Note: This is a placeholder since the actual method isn't exposed
        # In a real implementation, this would call the Go library
        return 0.0
    
    def get_matches(self, tokens: List[str], doc_id: str) -> List[TermMatch]:
        """
        Get term matches found in a specific document for the given tokens.
        
        Args:
            tokens: List of tokens to search for
            doc_id: Document ID to search in
            
        Returns:
            List of TermMatch objects for found terms
        """
        if not _lib:
            raise RuntimeError("BM25 library not available")
        
        # Convert tokens to JSON string
        tokens_json = json.dumps(tokens)
        
        # Call the GetMatches function
        result_ptr = _lib.GetMatches(
            ctypes.c_longlong(self.handle),
            tokens_json.encode('utf-8'),
            doc_id.encode('utf-8')
        )
        
        if not result_ptr:
            return []
        
        # Parse the results JSON
        try:
            result_json = ctypes.string_at(result_ptr).decode('utf-8')
            matches_data = json.loads(result_json)
            
            # Handle case where matches_data might be None or empty
            if not matches_data:
                return []
            
            # Convert to TermMatch objects
            matches = []
            for match_data in matches_data:
                match = TermMatch(
                    term=match_data.get('Term', ''),
                    frequency=match_data.get('Frequency', 0),
                    position=match_data.get('Position', -1)
                )
                matches.append(match)
            
            return matches
        except (json.JSONDecodeError, KeyError, TypeError):
            return []

class SmartTokenizer:
    """Smart tokenizer for text processing."""
    
    def __init__(self, language: str = "en"):
        """
        Initialize a smart tokenizer.
        
        Args:
            language: Language code for tokenization
        """
        if not _lib:
            raise RuntimeError("BM25 library not available")
        
        if language.lower() == "en":
            self.handle = _lib.CreateEnglishSmartTokenizer()
        else:
            self.handle = _lib.CreateSmartTokenizer(language.encode('utf-8'))
        
        if self.handle == 0:
            raise RuntimeError(f"Failed to create tokenizer for language: {language}")
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize the given text.
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of tokens
        """
        if not _lib:
            raise RuntimeError("BM25 library not available")
        
        result_ptr = _lib.TokenizeText(self.handle, text.encode('utf-8'))
        if result_ptr:
            result_json = ctypes.string_at(result_ptr).decode('utf-8')
            try:
                return json.loads(result_json)
            except json.JSONDecodeError:
                return []
        return []

class DefaultTokenizer:
    """Default tokenizer implementation."""
    
    def __init__(self):
        """Initialize the default tokenizer."""
        pass
    
    def tokenize(self, text: str) -> List[str]:
        """
        Simple tokenization by splitting on whitespace and punctuation.
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of tokens
        """
        import re
        # Simple tokenization: split on whitespace and punctuation
        tokens = re.findall(r'\b\w+\b', text.lower())
        return tokens

def hello_bm25() -> str:
    """Test function to verify the library is working."""
    if not _lib:
        raise RuntimeError("BM25 library not available")
    
    result_ptr = _lib.HelloBM25()
    if result_ptr:
        return ctypes.string_at(result_ptr).decode('utf-8')
    return ""

# Convenience functions
def new_bm25_index(doc_capacity: int = 1000, term_capacity: int = 10000) -> BM25Index:
    """Create a new BM25 index."""
    return BM25Index(doc_capacity, term_capacity)

def new_english_smart_tokenizer() -> SmartTokenizer:
    """Create a new English smart tokenizer."""
    return SmartTokenizer("en")

def new_smart_tokenizer(language: str) -> SmartTokenizer:
    """Create a new smart tokenizer for the specified language."""
    return SmartTokenizer(language)

def new_default_tokenizer() -> DefaultTokenizer:
    """Create a new default tokenizer."""
    return DefaultTokenizer()

def batch_search(index: BM25Index, queries: List[str], tokenizer, limit: int = 10) -> List[BatchSearchResult]:
    """Perform batch search on a BM25 index."""
    return index.batch_search(queries, tokenizer, limit)


# Export the main classes and functions for easy import
__all__ = ['BM25Index', 'SmartTokenizer', 'DefaultTokenizer', 'BatchSearchResult', 'TermMatch', 'hello_bm25', 
           'new_bm25_index', 'new_english_smart_tokenizer', 'new_smart_tokenizer', 'new_default_tokenizer',
           'batch_search']
