package main

import (
	"fmt"
	"log"

	"github.com/bm25"
)

func main() {
	fmt.Println("=== Compound Token Example ===\n")

	// Example 1: Medical Domain with Compound Terms
	fmt.Println("1. Medical Domain Example")
	fmt.Println("---------------------------")
	
	// Create tokenizer with medical compound words
	medicalCompounds := []string{
		"pulmonary edema",
		"heart failure", 
		"diabetes mellitus",
		"hypertension",
		"myocardial infarction",
	}
	
	medTokenizer := bm25.NewEnglishSmartTokenizerWithCompounds(medicalCompounds)
	
	// Create index
	index := bm25.NewIndex(100, 1000)
	
	// Add medical documents
	medicalDocs := []bm25.Document{
		{
			ID:      "med1",
			Content: "The patient presents with pulmonary edema and heart failure. Blood pressure indicates hypertension.",
		},
		{
			ID:      "med2", 
			Content: "Diabetes mellitus management with focus on preventing complications.",
		},
		{
			ID:      "med3",
			Content: "Acute myocardial infarction requires immediate intervention.",
		},
		{
			ID:      "med4",
			Content: "Simple edema without pulmonary involvement. No signs of heart failure.",
		},
	}
	
	for _, doc := range medicalDocs {
		err := index.AddDocument(doc.ID, doc.Content, medTokenizer)
		if err != nil {
			log.Fatal("Failed to add medical document:", err)
		}
	}
	
	// Test medical searches
	fmt.Println("Medical Search Results:")
	testMedicalSearches(index, medTokenizer)
	
	// Example 2: Technical Domain with Compound Terms
	fmt.Println("\n2. Technical Domain Example")
	fmt.Println("------------------------------")
	
	// Create tokenizer with technical compound words
	techCompounds := []string{
		"machine learning",
		"artificial intelligence", 
		"deep learning",
		"neural network",
		"natural language processing",
		"computer vision",
	}
	
	techTokenizer := bm25.NewEnglishSmartTokenizerWithCompounds(techCompounds)
	
	// Clear index for tech example
	index.Clear()
	
	// Add technical documents
	techDocs := []bm25.Document{
		{
			ID:      "tech1",
			Content: "Machine learning algorithms for natural language processing tasks.",
		},
		{
			ID:      "tech2",
			Content: "Deep learning approaches in computer vision applications.",
		},
		{
			ID:      "tech3", 
			Content: "Artificial intelligence and neural networks for pattern recognition.",
		},
		{
			ID:      "tech4",
			Content: "Simple learning without machine involvement. Basic neural processing.",
		},
	}
	
	for _, doc := range techDocs {
		err := index.AddDocument(doc.ID, doc.Content, techTokenizer)
		if err != nil {
			log.Fatal("Failed to add tech document:", err)
		}
	}
	
	// Test technical searches
	fmt.Println("Technical Search Results:")
	testTechnicalSearches(index, techTokenizer)
	
	// Example 3: Dynamic Compound Word Management
	fmt.Println("\n3. Dynamic Compound Word Management")
	fmt.Println("-------------------------------------")
	
	// Create base tokenizer
	baseTokenizer := bm25.NewEnglishSmartTokenizer()
	
	// Add compound words dynamically
	baseTokenizer.AddCompoundWord("pulmonary edema")
	baseTokenizer.AddCompoundWord("machine learning")
	
	// Show current compound words
	compounds := baseTokenizer.GetCompoundWords()
	fmt.Printf("Current compound words: %v\n", compounds)
	
	// Add more compound words
	baseTokenizer.AddCompoundWords([]string{"heart failure", "artificial intelligence"})
	
	// Show updated compound words
	compounds = baseTokenizer.GetCompoundWords()
	fmt.Printf("Updated compound words: %v\n", compounds)
	
	// Remove a compound word
	baseTokenizer.RemoveCompoundWord("pulmonary edema")
	compounds = baseTokenizer.GetCompoundWords()
	fmt.Printf("After removal: %v\n", compounds)
	
	// Example 4: Tokenization Details
	fmt.Println("\n4. Tokenization Details")
	fmt.Println("-------------------------")
	
	// Test tokenization with compound words
	testText := "The patient has pulmonary edema and uses machine learning algorithms"
	
	// Show tokenization with different tokenizers
	fmt.Printf("Original text: '%s'\n", testText)
	
	// No compound words
	simpleTokenizer := bm25.NewEnglishSmartTokenizer()
	simpleTokens := simpleTokenizer.Tokenize(testText)
	fmt.Printf("Simple tokenizer: %v\n", simpleTokens)
	
	// With compound words
	compoundTokenizer := bm25.NewEnglishSmartTokenizerWithCompounds([]string{"pulmonary edema", "machine learning"})
	compoundTokens := compoundTokenizer.Tokenize(testText)
	fmt.Printf("Compound tokenizer: %v\n", compoundTokens)
	
	fmt.Println("\n=== Compound Token Example Completed ===")
}

func testMedicalSearches(index *bm25.Index, tokenizer *bm25.SmartTokenizer) {
	queries := []string{
		"pulmonary edema",
		"pulmonary",
		"edema", 
		"heart failure",
		"heart",
		"failure",
		"diabetes mellitus",
		"hypertension",
	}
	
	for _, query := range queries {
		results := index.Search(query, tokenizer, 3)
		fmt.Printf("  '%s': %d results", query, len(results))
		
		if len(results) > 0 {
			fmt.Printf(" (top: %s, score: %.4f)", results[0].DocID, results[0].Score)
		}
		fmt.Println()
	}
}

func testTechnicalSearches(index *bm25.Index, tokenizer *bm25.SmartTokenizer) {
	queries := []string{
		"machine learning",
		"machine",
		"learning",
		"artificial intelligence", 
		"artificial",
		"intelligence",
		"deep learning",
		"neural network",
	}
	
	for _, query := range queries {
		results := index.Search(query, tokenizer, 3)
		fmt.Printf("  '%s': %d results", query, len(results))
		
		if len(results) > 0 {
			fmt.Printf(" (top: %s, score: %.4f)", results[0].DocID, results[0].Score)
		}
		fmt.Println()
	}
} 