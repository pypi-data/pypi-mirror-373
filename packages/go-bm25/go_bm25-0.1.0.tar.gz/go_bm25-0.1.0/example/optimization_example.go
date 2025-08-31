package main

import (
	"fmt"
	"log"
	"time"

	"github.com/bm25"
)

func runOptimizationExample() {
	fmt.Println("=== BM25 Optimization Example ===\n")

	// Example 1: Configurable BM25 Parameters
	fmt.Println("1. Configurable BM25 Parameters")
	fmt.Println("--------------------------------")
	
	// Create index with custom parameters (inspired by bm25s)
	customParams := bm25.BM25Params{
		K1:      1.5,    // Higher term frequency saturation
		B:       0.8,    // Stronger length normalization
		Epsilon: 0.1,    // Lower threshold for better precision
	}
	
	index := bm25.NewIndexWithParams(1000, 10000, customParams)
	fmt.Printf("Created index with K1=%.1f, B=%.1f, Epsilon=%.1f\n", 
		customParams.K1, customParams.B, customParams.Epsilon)
	
	// Example 2: Memory Pooling and Caching
	fmt.Println("\n2. Memory Pooling and Caching")
	fmt.Println("--------------------------------")
	
	// Create index with caching enabled
	cachedIndex := bm25.NewIndexWithCache(1000, 10000, 1000)
	fmt.Printf("Created cached index with cache size: %d\n", 1000)
	
	// Example 3: Bulk Document Addition
	fmt.Println("\n3. Bulk Document Addition")
	fmt.Println("---------------------------")
	
	// Generate sample documents
	documents := generateSampleDocuments(100)
	
	start := time.Now()
	err := index.BulkAddDocuments(documents, bm25.NewEnglishSmartTokenizer())
	if err != nil {
		log.Fatal("Failed to add documents:", err)
	}
	bulkTime := time.Since(start)
	
	fmt.Printf("Added %d documents in bulk: %v\n", len(documents), bulkTime)
	
	// Example 4: Different Search Methods
	fmt.Println("\n4. Search Method Comparison")
	fmt.Println("-----------------------------")
	
	queries := []string{
		"machine learning algorithm",
		"database system performance",
		"software development testing",
	}
	
	// Test different search methods
	for i, query := range queries {
		fmt.Printf("\nQuery %d: '%s'\n", i+1, query)
		
		// Standard search
		start := time.Now()
		results := index.Search(query, bm25.NewEnglishSmartTokenizer(), 5)
		standardTime := time.Since(start)
		fmt.Printf("  Standard search: %v, %d results\n", standardTime, len(results))
		
		// Optimized search
		start = time.Now()
		optimizedResults := index.SearchOptimized(query, bm25.NewEnglishSmartTokenizer(), 5)
		optimizedTime := time.Since(start)
		fmt.Printf("  Optimized search: %v, %d results\n", optimizedTime, len(optimizedResults))
		
		// Vectorized search
		start = time.Now()
		vectorizedResults := index.VectorizedSearch(query, bm25.NewEnglishSmartTokenizer(), 5)
		vectorizedTime := time.Since(start)
		fmt.Printf("  Vectorized search: %v, %d results\n", vectorizedTime, len(vectorizedResults))
		
		// Search with threshold
		start = time.Now()
		thresholdResults := index.SearchWithThreshold(query, bm25.NewEnglishSmartTokenizer(), 5, 0.1)
		thresholdTime := time.Since(start)
		fmt.Printf("  Threshold search: %v, %d results\n", thresholdTime, len(thresholdResults))
		
		// Show top result
		if len(results) > 0 {
			fmt.Printf("  Top result: %s (score: %.4f)\n", results[0].DocID, results[0].Score)
		}
	}
	
	// Example 5: Batch Search with Caching
	fmt.Println("\n5. Batch Search with Caching")
	fmt.Println("-------------------------------")
	
	// Enable caching
	cachedIndex.EnableCache(true)
	
	// Add documents to cached index
	err = cachedIndex.BulkAddDocuments(documents, bm25.NewEnglishSmartTokenizer())
	if err != nil {
		log.Fatal("Failed to add documents to cached index:", err)
	}
	
	// Perform batch search
	start = time.Now()
	batchResults := cachedIndex.BatchSearch(queries, bm25.NewEnglishSmartTokenizer(), 5)
	batchTime := time.Since(start)
	
	fmt.Printf("Batch search completed in: %v\n", batchTime)
	for i, result := range batchResults {
		fmt.Printf("  Query %d: %d results\n", i+1, len(result.Results))
	}
	
	// Example 6: Term Impact Analysis
	fmt.Println("\n6. Term Impact Analysis")
	fmt.Println("-------------------------")
	
	query := "machine learning algorithm"
	termImpacts := index.GetQueryTermsImpact(query, bm25.NewEnglishSmartTokenizer())
	
	fmt.Printf("Query: '%s'\n", query)
	fmt.Println("Terms sorted by impact:")
	for i, term := range termImpacts {
		impact := index.GetTermImpact(term)
		fmt.Printf("  %d. '%s' (impact: %.4f)\n", i+1, term, impact)
	}
	
	// Example 7: Performance Statistics
	fmt.Println("\n7. Performance Statistics")
	fmt.Println("--------------------------")
	
	stats := index.GetPerformanceStats()
	fmt.Printf("Total documents: %v\n", stats["total_documents"])
	fmt.Printf("Total terms: %v\n", stats["total_terms"])
	fmt.Printf("Average document length: %.2f\n", stats["average_document_length"])
	fmt.Printf("Estimated memory usage: %v MB\n", stats["memory_usage_mb"])
	
	// Example 8: Parameter Tuning
	fmt.Println("\n8. Parameter Tuning")
	fmt.Println("---------------------")
	
	// Test different parameter combinations
	paramCombinations := []bm25.BM25Params{
		{K1: 1.0, B: 0.5, Epsilon: 0.25},   // Conservative
		{K1: 1.2, B: 0.75, Epsilon: 0.25},  // Default
		{K1: 1.5, B: 0.8, Epsilon: 0.1},    // Aggressive
		{K1: 2.0, B: 0.9, Epsilon: 0.05},   // Very aggressive
	}
	
	query = "machine learning"
	fmt.Printf("Testing query: '%s'\n", query)
	
	for _, params := range paramCombinations {
		index.SetParameters(params)
		start := time.Now()
		results := index.Search(query, bm25.NewEnglishSmartTokenizer(), 3)
		searchTime := time.Since(start)
		
		fmt.Printf("  K1=%.1f, B=%.1f, Epsilon=%.2f: %v, %d results\n", 
			params.K1, params.B, params.Epsilon, searchTime, len(results))
		
		if len(results) > 0 {
			fmt.Printf("    Top score: %.4f\n", results[0].Score)
		}
	}
	
	fmt.Println("\n=== Optimization Example Completed ===")
}

// generateSampleDocuments creates sample documents for testing
func generateSampleDocuments(count int) []bm25.Document {
	topics := []string{
		"machine learning algorithm neural network deep learning",
		"database system performance optimization indexing",
		"software development testing deployment continuous integration",
		"web application framework frontend backend api",
		"data science analytics visualization statistics",
		"cloud computing infrastructure scalability microservices",
		"cybersecurity authentication encryption network security",
		"mobile development ios android cross platform",
		"artificial intelligence natural language processing",
		"blockchain cryptocurrency smart contract distributed ledger",
	}
	
	documents := make([]bm25.Document, count)
	for i := 0; i < count; i++ {
		topic := topics[i%len(topics)]
		documents[i] = bm25.Document{
			ID:      fmt.Sprintf("doc_%d", i),
			Content: fmt.Sprintf("Document %d about %s. This document discusses various aspects of %s including implementation details and best practices.", 
				i, topic, topic),
		}
	}
	
	return documents
} 