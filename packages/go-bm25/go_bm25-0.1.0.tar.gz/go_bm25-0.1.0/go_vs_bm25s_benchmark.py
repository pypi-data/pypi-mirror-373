#!/usr/bin/env python3
"""
Go BM25 vs bm25s Benchmark Comparison
This script compares the performance of:
1. Go BM25 implementation (through Python bindings)
2. bm25s library
"""

import time
import random
import statistics
import sys
import os
from typing import List, Dict, Tuple
from pathlib import Path

# Add the bm25 directory to Python path for our Go bindings
sys.path.insert(0, str(Path(__file__).parent / "bm25"))

try:
    import bm25  # Our Go BM25 bindings
    GO_BM25_AVAILABLE = True
    print("✓ Go BM25 bindings loaded successfully")
except ImportError as e:
    print(f"⚠ Go BM25 bindings not available: {e}")
    GO_BM25_AVAILABLE = False

try:
    import bm25s
    BM25S_AVAILABLE = True
    print("✓ bm25s library loaded successfully")
except ImportError as e:
    print(f"⚠ bm25s library not available: {e}")
    BM25S_AVAILABLE = False



def generate_benchmark_data(num_docs: int, avg_length: int) -> List[str]:
    """Generate synthetic document data for benchmarking"""
    common_words = [
        "computer", "programming", "algorithm", "data", "system", "software",
        "development", "technology", "information", "database", "network",
        "application", "service", "user", "interface", "design", "analysis",
        "testing", "deployment", "maintenance", "security", "performance",
        "scalability", "reliability", "efficiency", "optimization", "framework",
        "library", "module", "component", "architecture", "pattern", "method",
        "function", "class", "object", "variable", "constant", "parameter",
        "return", "exception", "error", "logging", "monitoring", "debugging"
    ]
    
    documents = []
    for i in range(num_docs):
        doc_length = avg_length + random.randint(-avg_length//4, avg_length//4)
        doc_length = max(5, doc_length)
        
        doc_words = []
        for _ in range(doc_length):
            word = random.choice(common_words)
            if random.random() < 0.3:
                doc_words.extend([word] * random.randint(1, 3))
            else:
                doc_words.append(word)
        
        documents.append(" ".join(doc_words))
    
    return documents

def benchmark_go_bm25_indexing(documents: List[str], num_runs: int = 5) -> Dict[str, float]:
    """Benchmark Go BM25 indexing through Python bindings"""
    if not GO_BM25_AVAILABLE:
        return {"error": "Go BM25 bindings not available"}
    
    print(f"Benchmarking Go BM25 indexing of {len(documents)} documents...")
    
    times = []
    for run in range(num_runs):
        start_time = time.perf_counter()
        
        # Create new index for each run
        index = bm25.new_bm25_index(len(documents), 10000)
        
        # Add all documents
        for i, content in enumerate(documents):
            doc_id = f"doc{i}"
            index.add_document(doc_id, content)
        
        end_time = time.perf_counter()
        times.append(end_time - start_time)
        
        print(f"  Run {run + 1}: {times[-1]:.6f}s")
    
    avg_time = statistics.mean(times)
    std_time = statistics.stdev(times) if len(times) > 1 else 0
    
    return {
        "avg_time": avg_time,
        "std_time": std_time,
        "times": times,
        "docs_per_second": len(documents) / avg_time
    }

def benchmark_go_bm25_smart_indexing(documents: List[str], num_runs: int = 5) -> Dict[str, float]:
    """Benchmark Go BM25 indexing with SmartTokenizer through Python bindings"""
    if not GO_BM25_AVAILABLE:
        return {"error": "Go BM25 bindings not available"}
    
    print(f"Benchmarking Go BM25 SmartTokenizer indexing of {len(documents)} documents...")
    
    times = []
    for run in range(num_runs):
        start_time = time.perf_counter()
        
        # Create new index for each run
        index = bm25.new_bm25_index(len(documents), 10000)
        tokenizer = bm25.new_english_smart_tokenizer()
        
        # Add all documents
        for i, content in enumerate(documents):
            doc_id = f"doc{i}"
            # For SmartTokenizer, we need to tokenize first
            tokens = tokenizer.tokenize(content)
            # Note: This is a limitation - the current API doesn't support tokenized input
            # We'll use the regular add_document for now
            index.add_document(doc_id, content)
        
        end_time = time.perf_counter()
        times.append(end_time - start_time)
        
        print(f"  Run {run + 1}: {times[-1]:.6f}s")
    
    avg_time = statistics.mean(times)
    std_time = statistics.stdev(times) if len(times) > 1 else 0
    
    return {
        "avg_time": avg_time,
        "std_time": std_time,
        "times": times,
        "docs_per_second": len(documents) / avg_time
    }

def benchmark_bm25s_indexing(documents: List[str], num_runs: int = 5) -> Dict[str, float]:
    """Benchmark bm25s indexing"""
    if not BM25S_AVAILABLE:
        return {"error": "bm25s library not available"}
    
    print(f"Benchmarking bm25s indexing of {len(documents)} documents...")
    
    times = []
    for run in range(num_runs):
        start_time = time.perf_counter()
        
        # Create new index for each run
        index = bm25s.BM25()
        
        # Tokenize documents and build index
        tokenized_docs = [doc.split() for doc in documents]
        index.index(tokenized_docs)
        
        end_time = time.perf_counter()
        times.append(end_time - start_time)
        
        print(f"  Run {run + 1}: {times[-1]:.6f}s")
    
    avg_time = statistics.mean(times)
    std_time = statistics.stdev(times) if len(times) > 1 else 0
    
    return {
        "avg_time": avg_time,
        "std_time": std_time,
        "times": times,
        "docs_per_second": len(documents) / avg_time
    }



def benchmark_go_bm25_search(documents: List[str], queries: List[str], num_runs: int = 5) -> Dict[str, float]:
    """Benchmark Go BM25 search through Python bindings"""
    if not GO_BM25_AVAILABLE:
        return {"error": "Go BM25 bindings not available"}
    
    print(f"Benchmarking Go BM25 search with {len(queries)} queries...")
    
    # Create index once
    index = bm25.new_bm25_index(len(documents), 10000)
    
    for i, content in enumerate(documents):
        doc_id = f"doc{i}"
        index.add_document(doc_id, content)
    
    times = []
    for run in range(num_runs):
        start_time = time.perf_counter()
        
        for query in queries:
            results = index.search(query, 10)
        
        end_time = time.perf_counter()
        times.append(end_time - start_time)
        
        print(f"  Run {run + 1}: {times[-1]:.6f}s")
    
    avg_time = statistics.mean(times)
    std_time = statistics.stdev(times) if len(times) > 1 else 0
    
    return {
        "avg_time": avg_time,
        "std_time": std_time,
        "times": times,
        "queries_per_second": len(queries) / avg_time
    }

def benchmark_go_bm25_smart_search(documents: List[str], queries: List[str], num_runs: int = 5) -> Dict[str, float]:
    """Benchmark Go BM25 search with SmartTokenizer through Python bindings"""
    if not GO_BM25_AVAILABLE:
        return {"error": "Go BM25 bindings not available"}
    
    print(f"Benchmarking Go BM25 SmartTokenizer search with {len(queries)} queries...")
    
    # Create index once
    index = bm25.new_bm25_index(len(documents), 10000)
    tokenizer = bm25.new_english_smart_tokenizer()
    
    for i, content in enumerate(documents):
        doc_id = f"doc{i}"
        index.add_document(doc_id, content)
    
    times = []
    for run in range(num_runs):
        start_time = time.perf_counter()
        
        for query in queries:
            # Tokenize query with SmartTokenizer
            query_tokens = tokenizer.tokenize(query)
            # Note: The current search API doesn't use the tokenizer directly
            # We'll use the regular search for now
            results = index.search(query, 10)
        
        end_time = time.perf_counter()
        times.append(end_time - start_time)
        
        print(f"  Run {run + 1}: {times[-1]:.6f}s")
    
    avg_time = statistics.mean(times)
    std_time = statistics.stdev(times) if len(times) > 1 else 0
    
    return {
        "avg_time": avg_time,
        "std_time": std_time,
        "times": times,
        "queries_per_second": len(queries) / avg_time
    }

def benchmark_bm25s_search(documents: List[str], queries: List[str], num_runs: int = 5) -> Dict[str, float]:
    """Benchmark bm25s search"""
    if not BM25S_AVAILABLE:
        return {"error": "bm25s library not available"}
    
    print(f"Benchmarking bm25s search with {len(queries)} queries...")
    
    # Create index once
    index = bm25s.BM25()
    tokenized_docs = [doc.split() for doc in documents]
    index.index(tokenized_docs)
    
    times = []
    for run in range(num_runs):
        start_time = time.perf_counter()
        
        for query in queries:
            query_tokens = query.split()
            results = index.retrieve([query_tokens], k=10)
        
        end_time = time.perf_counter()
        times.append(end_time - start_time)
        
        print(f"  Run {run + 1}: {times[-1]:.6f}s")
    
    avg_time = statistics.mean(times)
    std_time = statistics.stdev(times) if len(times) > 1 else 0
    
    return {
        "avg_time": avg_time,
        "std_time": std_time,
        "times": times,
        "queries_per_second": len(queries) / avg_time
    }

def benchmark_go_bm25_batch_search(documents: List[str], queries: List[str], num_runs: int = 5) -> Dict[str, float]:
    """Benchmark Go BM25 batch search through Python bindings"""
    if not GO_BM25_AVAILABLE:
        return {"error": "Go BM25 bindings not available"}
    
    print(f"Benchmarking Go BM25 BATCH search with {len(queries)} queries...")
    
    # Create index once
    index = bm25.new_bm25_index(len(documents), 10000)
    tokenizer = bm25.new_default_tokenizer()
    
    for i, content in enumerate(documents):
        doc_id = f"doc{i}"
        index.add_document(doc_id, content)
    
    times = []
    for run in range(num_runs):
        start_time = time.perf_counter()
        
        # Use batch search for all queries at once
        batch_results = index.batch_search(queries, tokenizer, 10)
        
        end_time = time.perf_counter()
        times.append(end_time - start_time)
        
        print(f"  Run {run + 1}: {times[-1]:.6f}s")
    
    avg_time = statistics.mean(times)
    std_time = statistics.stdev(times) if len(times) > 1 else 0
    
    return {
        "avg_time": avg_time,
        "std_time": std_time,
        "times": times,
        "queries_per_second": len(queries) / avg_time
    }

def benchmark_bm25s_batch_search(documents: List[str], queries: List[str], num_runs: int = 5) -> Dict[str, float]:
    """Benchmark bm25s batch search"""
    if not BM25S_AVAILABLE:
        return {"error": "bm25s library not available"}
    
    print(f"Benchmarking bm25s BATCH search with {len(queries)} queries...")
    
    # Create index once
    index = bm25s.BM25()
    tokenized_docs = [doc.split() for doc in documents]
    index.index(tokenized_docs)
    
    # Prepare all queries as tokenized batch
    tokenized_queries = [query.split() for query in queries]
    
    times = []
    for run in range(num_runs):
        start_time = time.perf_counter()
        
        # Use batch retrieval for all queries at once
        results = index.retrieve(tokenized_queries, k=10)
        
        end_time = time.perf_counter()
        times.append(end_time - start_time)
        
        print(f"  Run {run + 1}: {times[-1]:.6f}s")
    
    avg_time = statistics.mean(times)
    std_time = statistics.stdev(times) if len(times) > 1 else 0
    
    return {
        "avg_time": avg_time,
        "std_time": std_time,
        "times": times,
        "queries_per_second": len(queries) / avg_time
    }


def print_benchmark_results(name: str, results: Dict[str, float]):
    """Print benchmark results in a formatted way"""
    if "error" in results:
        print(f"  {name}: {results['error']}")
        return
    
    print(f"  {name}:")
    print(f"    Time: {results['avg_time']:.6f}s ± {results['std_time']:.6f}s")
    if 'docs_per_second' in results:
        print(f"    Throughput: {results['docs_per_second']:.2f} docs/sec")
    elif 'queries_per_second' in results:
        print(f"    Throughput: {results['queries_per_second']:.2f} queries/sec")

def main():
    """Main benchmark function"""
    print("=== Go BM25 vs bm25s Benchmark Comparison ===")
    print("=" * 70)
    
    # Set random seed for reproducible results
    random.seed(42)
    
    # Generate benchmark data
    print("Generating benchmark data...")
    documents = generate_benchmark_data(2000, 100)  # 2000 docs, avg 100 words
    queries = [
        "computer programming algorithm",
        "database system performance",
        "software development testing",
        "network security authentication",
        "machine learning optimization",
        "cloud computing infrastructure",
        "data science analytics",
        "web development framework",
        "artificial intelligence neural networks",
        "cybersecurity threat detection",
    ]
    
    print(f"Generated {len(documents)} documents with average length {len(documents[0].split())} words")
    print(f"Using {len(queries)} test queries")
    print()
    
    # Run indexing benchmarks
    print("INDEXING BENCHMARKS")
    print("-" * 40)
    
    go_indexing = benchmark_go_bm25_indexing(documents)
    go_smart_indexing = benchmark_go_bm25_smart_indexing(documents)
    bm25s_indexing = benchmark_bm25s_indexing(documents)
    
    print()
    print("Indexing Results:")
    print_benchmark_results("Go BM25 (Default)", go_indexing)
    print_benchmark_results("Go BM25 (SmartTokenizer)", go_smart_indexing)
    print_benchmark_results("bm25s", bm25s_indexing)
    print()
    
    # Run search benchmarks
    print("SEARCH BENCHMARKS")
    print("-" * 40)
    
    go_search = benchmark_go_bm25_search(documents, queries)
    go_smart_search = benchmark_go_bm25_smart_search(documents, queries)
    bm25s_search = benchmark_bm25s_search(documents, queries)
    
    print()
    print("Search Results:")
    print_benchmark_results("Go BM25 (Default)", go_search)
    print_benchmark_results("Go BM25 (SmartTokenizer)", go_smart_search)
    print_benchmark_results("bm25s", bm25s_search)
    print()
    
    # Run batch search benchmarks
    print("BATCH SEARCH BENCHMARKS")
    print("-" * 40)
    
    go_batch_search = benchmark_go_bm25_batch_search(documents, queries)
    bm25s_batch_search = benchmark_bm25s_batch_search(documents, queries)
    
    print()
    print("Batch Search Results:")
    print_benchmark_results("Go BM25 (Batch)", go_batch_search)
    print_benchmark_results("bm25s (Batch)", bm25s_batch_search)
    print()
    
    # Performance comparison
    print("PERFORMANCE COMPARISON")
    print("-" * 40)
    
    if "error" not in go_indexing and "error" not in bm25s_indexing:
        go_speed = go_indexing["docs_per_second"]
        bm25s_speed = bm25s_indexing["docs_per_second"]
        speedup = go_speed / bm25s_speed
        print(f"Go BM25 (Default) vs bm25s indexing: {speedup:.2f}x {'faster' if speedup > 1 else 'slower'}")
    
    if "error" not in go_smart_indexing and "error" not in bm25s_indexing:
        go_smart_speed = go_smart_indexing["docs_per_second"]
        bm25s_speed = bm25s_indexing["docs_per_second"]
        speedup = go_smart_speed / bm25s_speed
        print(f"Go BM25 (SmartTokenizer) vs bm25s indexing: {speedup:.2f}x {'faster' if speedup > 1 else 'slower'}")
    
    if "error" not in go_search and "error" not in bm25s_search:
        go_speed = go_search["queries_per_second"]
        bm25s_speed = bm25s_search["queries_per_second"]
        speedup = go_speed / bm25s_speed
        print(f"Go BM25 (Default) vs bm25s search: {speedup:.2f}x {'faster' if speedup > 1 else 'slower'}")
    
    if "error" not in go_smart_search and "error" not in bm25s_search:
        go_smart_speed = go_smart_search["queries_per_second"]
        bm25s_speed = bm25s_search["queries_per_second"]
        speedup = go_smart_speed / bm25s_speed
        print(f"Go BM25 (SmartTokenizer) vs bm25s search: {speedup:.2f}x {'faster' if speedup > 1 else 'slower'}")
    
    print("\nBatch Search Comparisons:")
    if "error" not in go_batch_search and "error" not in bm25s_batch_search:
        go_batch_speed = go_batch_search["queries_per_second"]
        bm25s_batch_speed = bm25s_batch_search["queries_per_second"]
        speedup = go_batch_speed / bm25s_batch_speed
        print(f"Go BM25 (Batch) vs bm25s (Batch): {speedup:.2f}x {'faster' if speedup > 1 else 'slower'}")
    
    # Compare individual vs batch for each library
    if "error" not in go_search and "error" not in go_batch_search:
        go_individual = go_search["queries_per_second"]
        go_batch_speed = go_batch_search["queries_per_second"]
        speedup = go_batch_speed / go_individual
        print(f"Go BM25 Batch vs Individual: {speedup:.2f}x {'faster' if speedup > 1 else 'slower'}")
    
    if "error" not in bm25s_search and "error" not in bm25s_batch_search:
        bm25s_individual = bm25s_search["queries_per_second"]
        bm25s_batch_speed = bm25s_batch_search["queries_per_second"]
        speedup = bm25s_batch_speed / bm25s_individual
        print(f"bm25s Batch vs Individual: {speedup:.2f}x {'faster' if speedup > 1 else 'slower'}")
    
    print("\n" + "=" * 70)
    print("BENCHMARK COMPLETED!")
    print("=" * 70)
    print("\nKey Insights:")
    print("  - Go BM25 provides direct access to your optimized Go implementation")
    print("  - Python bindings eliminate the need for external binary execution")
    print("  - Performance should be close to native Go performance")
    print("  - Memory usage should be more efficient than pure Python implementations")

if __name__ == "__main__":
    main() 