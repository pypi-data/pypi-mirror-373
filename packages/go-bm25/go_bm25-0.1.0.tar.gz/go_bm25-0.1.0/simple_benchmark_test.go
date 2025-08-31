package bm25

import (
	"fmt"
	"testing"
)

// Benchmark different search methods
func BenchmarkSearchMethods(b *testing.B) {
	// Create test index
	index := NewIndex(1000, 10000)
	tokenizer := NewEnglishSmartTokenizer()
	
	// Add test documents
	documents := generateBenchmarkDocuments(100)
	for _, doc := range documents {
		index.AddDocument(doc.ID, doc.Content, tokenizer)
	}
	
	query := "machine learning algorithm"
	
	b.Run("StandardSearch", func(b *testing.B) {
		for i := 0; i < b.N; i++ {
			index.Search(query, tokenizer, 10)
		}
	})
	
	b.Run("OptimizedSearch", func(b *testing.B) {
		for i := 0; i < b.N; i++ {
			index.SearchOptimized(query, tokenizer, 10)
		}
	})
	
	b.Run("VectorizedSearch", func(b *testing.B) {
		for i := 0; i < b.N; i++ {
			index.VectorizedSearch(query, tokenizer, 10)
		}
	})
	
	b.Run("SearchWithThreshold", func(b *testing.B) {
		for i := 0; i < b.N; i++ {
			index.SearchWithThreshold(query, tokenizer, 10, 0.1)
		}
	})
}

// Benchmark different parameter configurations
func BenchmarkParameterConfigurations(b *testing.B) {
	// Test different parameter combinations
	configs := []BM25Params{
		{K1: 1.0, B: 0.5, Epsilon: 0.25},   // Conservative
		{K1: 1.2, B: 0.75, Epsilon: 0.25},  // Default
		{K1: 1.5, B: 0.8, Epsilon: 0.1},    // Aggressive
		{K1: 2.0, B: 0.9, Epsilon: 0.05},   // Very aggressive
	}
	
	for _, config := range configs {
		b.Run(fmt.Sprintf("K1_%.1f_B_%.1f_Epsilon_%.2f", config.K1, config.B, config.Epsilon), func(b *testing.B) {
			index := NewIndexWithParams(1000, 10000, config)
			tokenizer := NewEnglishSmartTokenizer()
			
			// Add test documents
			documents := generateBenchmarkDocuments(100)
			for _, doc := range documents {
				index.AddDocument(doc.ID, doc.Content, tokenizer)
			}
			
			query := "machine learning algorithm"
			b.ResetTimer()
			
			for i := 0; i < b.N; i++ {
				index.Search(query, tokenizer, 10)
			}
		})
	}
}

// Benchmark caching performance
func BenchmarkCaching(b *testing.B) {
	// Create cached index
	index := NewIndexWithCache(1000, 10000, 1000)
	tokenizer := NewEnglishSmartTokenizer()
	
	// Add test documents
	documents := generateBenchmarkDocuments(100)
	for _, doc := range documents {
		index.AddDocument(doc.ID, doc.Content, tokenizer)
	}
	
	queries := []string{
		"machine learning algorithm",
		"database system performance",
		"software development testing",
	}
	
	b.Run("WithoutCache", func(b *testing.B) {
		index.EnableCache(false)
		for i := 0; i < b.N; i++ {
			query := queries[i%len(queries)]
			index.Search(query, tokenizer, 10)
		}
	})
	
	b.Run("WithCache", func(b *testing.B) {
		index.EnableCache(true)
		// Warm up cache
		for _, query := range queries {
			index.Search(query, tokenizer, 10)
		}
		
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			query := queries[i%len(queries)]
			index.SearchWithCache(query, tokenizer, 10)
		}
	})
}

// Benchmark batch operations
func BenchmarkBatchOperations(b *testing.B) {
	// Test different batch sizes
	batchSizes := []int{10, 50, 100}
	
	for _, batchSize := range batchSizes {
		b.Run(fmt.Sprintf("BatchSize_%d", batchSize), func(b *testing.B) {
			index := NewIndex(1000, 10000)
			tokenizer := NewEnglishSmartTokenizer()
			
			// Generate documents for this batch size
			documents := generateBenchmarkDocuments(batchSize)
			
			b.ResetTimer()
			for i := 0; i < b.N; i++ {
				index.Clear()
				index.BulkAddDocuments(documents, tokenizer)
			}
		})
	}
}

// Benchmark early termination effectiveness
func BenchmarkEarlyTermination(b *testing.B) {
	// Create index with different epsilon values
	epsilonValues := []float64{0.05, 0.1, 0.25, 0.5}
	
	for _, epsilon := range epsilonValues {
		b.Run(fmt.Sprintf("Epsilon_%.2f", epsilon), func(b *testing.B) {
			params := BM25Params{
				K1:      1.2,
				B:       0.75,
				Epsilon: epsilon,
			}
			
			index := NewIndexWithParams(1000, 10000, params)
			tokenizer := NewEnglishSmartTokenizer()
			
			// Add test documents
			documents := generateBenchmarkDocuments(100)
			for _, doc := range documents {
				index.AddDocument(doc.ID, doc.Content, tokenizer)
			}
			
			query := "machine learning algorithm neural network deep learning artificial intelligence"
			b.ResetTimer()
			
			for i := 0; i < b.N; i++ {
				index.SearchOptimized(query, tokenizer, 5)
			}
		})
	}
}

// Helper function to generate benchmark documents
func generateBenchmarkDocuments(count int) []Document {
	topics := []string{
		"machine learning algorithm neural network deep learning artificial intelligence",
		"database system performance optimization indexing query optimization",
		"software development testing deployment continuous integration devops",
		"web application framework frontend backend api microservices",
		"data science analytics visualization statistics big data",
		"cloud computing infrastructure scalability microservices kubernetes",
		"cybersecurity authentication encryption network security blockchain",
		"mobile development ios android cross platform react native",
		"natural language processing text mining sentiment analysis",
		"distributed systems consensus algorithms fault tolerance",
	}
	
	documents := make([]Document, count)
	for i := 0; i < count; i++ {
		topic := topics[i%len(topics)]
		documents[i] = Document{
			ID:      fmt.Sprintf("doc_%d", i),
			Content: fmt.Sprintf("Document %d about %s. This comprehensive document discusses various aspects of %s including implementation details, best practices, and real-world applications. The content covers theoretical foundations, practical considerations, and performance optimization techniques.", 
				i, topic, topic),
		}
	}
	
	return documents
} 