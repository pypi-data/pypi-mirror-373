"""
BM25 Python Package

High-performance BM25 ranking algorithm implementation with Go core and Python bindings.
"""

from .bm25 import (
    BM25Index,
    SmartTokenizer,
    DefaultTokenizer,
    BatchSearchResult,
    hello_bm25,
    new_bm25_index,
    new_english_smart_tokenizer,
    new_smart_tokenizer,
    new_default_tokenizer,
    batch_search,
)

from .bm25s_compat import (
    BM25 as BM25Compat,
    tokenize,
)

__version__ = "0.1.0"
__author__ = "BM25 Contributors"

__all__ = [
    "BM25Index",
    "SmartTokenizer", 
    "DefaultTokenizer",
    "BatchSearchResult",
    "hello_bm25",
    "new_bm25_index",
    "new_english_smart_tokenizer",
    "new_smart_tokenizer",
    "new_default_tokenizer",
    "batch_search",
    "BM25Compat",
    "tokenize",
]
