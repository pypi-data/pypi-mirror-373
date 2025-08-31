package main

import (
	"C"
	"container/heap"
	"errors"
	"fmt"
	"math"
	"sort"
	"strings"
	"sync"
	"unicode"
)

// BM25 parameters with configurable values
type BM25Params struct {
	K1      float64 // Term frequency saturation parameter (default: 1.2)
	B       float64 // Length normalization parameter (default: 0.75)
	Epsilon float64 // Minimum score threshold for early termination (default: 0.25)
}

// Default BM25 parameters
var DefaultBM25Params = BM25Params{
	K1:      1.2,
	B:       0.75,
	Epsilon: 0.25,
}

// TermEntry represents a term in the index with its document occurrences
type TermEntry struct {
	Term       string
	DocCount   int
	DocIDs     []int
	TermCounts []int
	IDF        float64 // Precomputed IDF value for optimization
}

// DocumentEntry represents a document with its terms and frequencies
type DocumentEntry struct {
	DocID       string
	TotalTerms  int
	UniqueTerms int
	Terms       []string
	TermFreqs   []int
}

// Document represents a document to be added to the index
type Document struct {
	ID      string
	Content string
}

// SearchResult represents a search result with document ID and BM25 score
type SearchResult struct {
	DocID string
	Score float64
}

// TermIDFPair represents a term and its inverse document frequency
type TermIDFPair struct {
	Term     string
	IDF      float64
	DocCount int // Number of documents containing this term
}

// TermIDFIterator provides an interface for iterating over term-IDF pairs
type TermIDFIterator struct {
	index    *Index
	position int
	current  *TermIDFPair
}

// SearchResultHeap implements heap.Interface for efficient top-k selection
type SearchResultHeap []SearchResult

func (h SearchResultHeap) Len() int           { return len(h) }
func (h SearchResultHeap) Less(i, j int) bool { return h[i].Score < h[j].Score }
func (h SearchResultHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }

func (h *SearchResultHeap) Push(x interface{}) {
	*h = append(*h, x.(SearchResult))
}

func (h *SearchResultHeap) Pop() interface{} {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[0 : n-1]
	return x
}

// BatchSearchResult represents a batch search result
type BatchSearchResult struct {
	Query   string
	Results []SearchResult
}

// SearchCache provides fast in-memory caching for search results
type SearchCache struct {
	cache   map[string][]SearchResult
	mutex   sync.RWMutex
	maxSize int
	stats   *CacheStats
}

// NewSearchCache creates a new search cache with specified maximum size
func NewSearchCache(maxSize int) *SearchCache {
	return &SearchCache{
		cache:   make(map[string][]SearchResult),
		maxSize: maxSize,
		stats:   NewCacheStats(),
	}
}

// Get retrieves cached results for a query
func (sc *SearchCache) Get(query string) ([]SearchResult, bool) {
	sc.mutex.RLock()
	defer sc.mutex.RUnlock()
	results, exists := sc.cache[query]
	if exists {
		sc.stats.RecordHit()
	} else {
		sc.stats.RecordMiss()
	}
	return results, exists
}

// Set stores results in the cache
func (sc *SearchCache) Set(query string, results []SearchResult) {
	sc.mutex.Lock()
	defer sc.mutex.Unlock()

	// Implement LRU-like eviction if cache is full
	if len(sc.cache) >= sc.maxSize {
		// Simple eviction: remove a random entry (in practice, you might want LRU)
		for k := range sc.cache {
			delete(sc.cache, k)
			break
		}
	}

	sc.cache[query] = results
}

// Clear removes all cached results
func (sc *SearchCache) Clear() {
	sc.mutex.Lock()
	defer sc.mutex.Unlock()
	sc.cache = make(map[string][]SearchResult)
}

// GetStats returns cache performance statistics
func (sc *SearchCache) GetStats() map[string]interface{} {
	stats := make(map[string]interface{})
	stats["hit_rate"] = sc.stats.GetHitRate()
	stats["size"] = len(sc.cache)
	stats["max_size"] = sc.maxSize
	return stats
}

// CacheStats tracks cache performance metrics
type CacheStats struct {
	hits   int64
	misses int64
	mutex  sync.RWMutex
}

// NewCacheStats creates new cache statistics
func NewCacheStats() *CacheStats {
	return &CacheStats{}
}

// RecordHit records a cache hit
func (cs *CacheStats) RecordHit() {
	cs.mutex.Lock()
	defer cs.mutex.Unlock()
	cs.hits++
}

// RecordMiss records a cache miss
func (cs *CacheStats) RecordMiss() {
	cs.mutex.Lock()
	defer cs.mutex.Unlock()
	cs.misses++
}

// GetHitRate returns the hit rate
func (cs *CacheStats) GetHitRate() float64 {
	cs.mutex.RLock()
	defer cs.mutex.RUnlock()

	total := cs.hits + cs.misses
	if total == 0 {
		return 0.0
	}
	return float64(cs.hits) / float64(total)
}

// Index represents the BM25 index with configurable parameters
type Index struct {
	termIndex      []*TermEntry
	docIndex       []*DocumentEntry
	termMap        map[string]int // term -> termIndex position
	docMap         map[string]int // docID -> docIndex position
	termCapacity   int
	docCapacity    int
	totalDocuments int
	avgDocLength   float64
	statsComputed  bool         // Flag to track if statistics are up to date
	params         BM25Params   // Configurable BM25 parameters
	scorePool      sync.Pool    // Memory pool for score maps
	searchCache    *SearchCache // Optional search result cache
	cacheEnabled   bool         // Whether caching is enabled
}

// Tokenizer interface for custom tokenization
type Tokenizer interface {
	Tokenize(text string) []string
}

// DefaultTokenizer implements basic whitespace-based tokenization
type DefaultTokenizer struct{}

// NewIndex creates a new BM25 index with specified capacities and default parameters
func NewIndex(docCapacity, termCapacity int) *Index {
	return NewIndexWithParams(docCapacity, termCapacity, DefaultBM25Params)
}

// NewIndexWithParams creates a new BM25 index with custom parameters
func NewIndexWithParams(docCapacity, termCapacity int, params BM25Params) *Index {
	return &Index{
		termIndex:     make([]*TermEntry, 0, termCapacity),
		docIndex:      make([]*DocumentEntry, 0, docCapacity),
		termMap:       make(map[string]int),
		docMap:        make(map[string]int),
		termCapacity:  termCapacity,
		docCapacity:   docCapacity,
		statsComputed: false,
		params:        params,
		scorePool: sync.Pool{
			New: func() interface{} {
				return make(map[int]float64, 1000) // Pre-allocate with reasonable capacity
			},
		},
	}
}

// NewIndexWithCache creates a new BM25 index with search result caching
func NewIndexWithCache(docCapacity, termCapacity int, cacheSize int) *Index {
	index := NewIndexWithParams(docCapacity, termCapacity, DefaultBM25Params)
	index.searchCache = NewSearchCache(cacheSize)
	index.cacheEnabled = true
	return index
}

// NewIndexWithMultiLevelCache creates a new BM25 index with search result caching
func NewIndexWithMultiLevelCache(docCapacity, termCapacity int, cacheSize int) *Index {
	index := NewIndexWithParams(docCapacity, termCapacity, DefaultBM25Params)
	index.searchCache = NewSearchCache(cacheSize)
	index.cacheEnabled = true
	return index
}

// EnableCache enables or disables search result caching
func (idx *Index) EnableCache(enable bool) {
	idx.cacheEnabled = enable
	if !enable && idx.searchCache != nil {
		idx.searchCache.Clear()
	}
}

// SetCacheSize sets the maximum size of the search cache
func (idx *Index) SetCacheSize(size int) {
	if idx.searchCache != nil {
		idx.searchCache.maxSize = size
	}
}

// SetParameters updates the BM25 parameters for the index
func (idx *Index) SetParameters(params BM25Params) {
	idx.params = params
	// Parameters changed, so we need to recompute statistics
	idx.statsComputed = false
}

// GetParameters returns the current BM25 parameters
func (idx *Index) GetParameters() BM25Params {
	return idx.params
}

// AddDocument adds a document to the index using a tokenizer
func (idx *Index) AddDocument(docID string, content string, tokenizer Tokenizer) error {
	if len(idx.docIndex) >= idx.docCapacity {
		return ErrCapacityExceeded
	}

	// Tokenize the document
	terms := tokenizer.Tokenize(content)

	// Create document entry
	docEntry := &DocumentEntry{
		DocID:       docID,
		TotalTerms:  len(terms),
		UniqueTerms: 0,
		Terms:       make([]string, 0, len(terms)),
		TermFreqs:   make([]int, 0, len(terms)),
	}

	// Count term frequencies and handle compound terms
	termFreqs := make(map[string]int)
	for _, term := range terms {
		termFreqs[term]++
	}

	// Build term arrays
	for term, freq := range termFreqs {
		docEntry.Terms = append(docEntry.Terms, term)
		docEntry.TermFreqs = append(docEntry.TermFreqs, freq)
	}
	docEntry.UniqueTerms = len(docEntry.Terms)

	// Add document to index
	docPos := len(idx.docIndex)
	idx.docIndex = append(idx.docIndex, docEntry)
	idx.docMap[docID] = docPos

	// Update term index
	for i, term := range docEntry.Terms {
		freq := docEntry.TermFreqs[i]

		// Find or create term entry
		termPos, exists := idx.termMap[term]
		if !exists {
			termEntry := &TermEntry{
				Term:       term,
				DocCount:   0,
				DocIDs:     make([]int, 0, 10),
				TermCounts: make([]int, 0, 10),
			}
			termPos = len(idx.termIndex)
			idx.termIndex = append(idx.termIndex, termEntry)
			idx.termMap[term] = termPos
		}

		// Update term entry
		termEntry := idx.termIndex[termPos]
		termEntry.DocCount++
		termEntry.DocIDs = append(termEntry.DocIDs, docPos)
		termEntry.TermCounts = append(termEntry.TermCounts, freq)
	}

	// Mark statistics as needing recomputation
	idx.statsComputed = false

	return nil
}

// Search performs a BM25 search and returns ranked results
func (idx *Index) Search(query string, tokenizer Tokenizer, limit int) []SearchResult {
	// Ensure statistics are computed
	idx.computeStatistics()

	queryTerms := tokenizer.Tokenize(query)

	// Early termination for empty queries
	if len(queryTerms) == 0 {
		return []SearchResult{}
	}

	// Get score map from pool
	docScores := idx.scorePool.Get().(map[int]float64)
	defer func() {
		// Clear and return to pool
		for k := range docScores {
			delete(docScores, k)
		}
		idx.scorePool.Put(docScores)
	}()

	// Calculate scores for each document
	for _, term := range queryTerms {
		if termPos, exists := idx.termMap[term]; exists {
			termEntry := idx.termIndex[termPos]

			// Use precomputed IDF instead of calculating it
			idf := termEntry.IDF

			// Calculate scores for documents containing this term
			for i, docPos := range termEntry.DocIDs {
				termFreq := termEntry.TermCounts[i]
				docScore := idx.calculateBM25Score(termFreq, docPos, idf)
				docScores[docPos] += docScore
			}
		}
	}

	// Use heap-based top-k selection for better performance
	if limit > 0 && limit < len(docScores) {
		return idx.selectTopK(docScores, limit)
	}

	// Convert all scores to results and sort (for small result sets)
	results := make([]SearchResult, 0, len(docScores))
	for docPos, score := range docScores {
		if docPos < len(idx.docIndex) {
			results = append(results, SearchResult{
				DocID: idx.docIndex[docPos].DocID,
				Score: score,
			})
		}
	}

	// Sort by score (descending)
	sort.Slice(results, func(i, j int) bool {
		return results[i].Score > results[j].Score
	})

	return results
}

// selectTopK efficiently selects top-k results using a min-heap
func (idx *Index) selectTopK(docScores map[int]float64, k int) []SearchResult {
	h := &SearchResultHeap{}
	heap.Init(h)

	// Build min-heap with top-k scores
	for docPos, score := range docScores {
		if docPos >= len(idx.docIndex) {
			continue
		}

		result := SearchResult{
			DocID: idx.docIndex[docPos].DocID,
			Score: score,
		}

		if h.Len() < k {
			heap.Push(h, result)
		} else if score > (*h)[0].Score {
			// Replace smallest score with larger one
			heap.Pop(h)
			heap.Push(h, result)
		}
	}

	// Extract results in descending order
	results := make([]SearchResult, h.Len())
	for i := len(results) - 1; i >= 0; i-- {
		results[i] = heap.Pop(h).(SearchResult)
	}

	return results
}

// calculateBM25Score calculates the BM25 score for a term in a document
func (idx *Index) calculateBM25Score(termFreq int, docPos int, idf float64) float64 {
	if idx.avgDocLength <= 0 {
		return 0.0
	}

	docLength := float64(idx.docIndex[docPos].TotalTerms)
	normalizedLength := docLength / idx.avgDocLength

	numerator := float64(termFreq) * (idx.params.K1 + 1.0)
	denominator := float64(termFreq) + idx.params.K1*(1.0-idx.params.B+idx.params.B*normalizedLength)

	return idf * numerator / denominator
}

// calculateIDF calculates the Inverse Document Frequency with epsilon smoothing
func (idx *Index) calculateIDF(docCount int) float64 {
	if docCount <= 0 || idx.totalDocuments <= 0 {
		return 0.0
	}

	// Apply epsilon smoothing to prevent division by zero and improve stability
	numerator := float64(idx.totalDocuments) - float64(docCount) + idx.params.Epsilon
	denominator := float64(docCount) + idx.params.Epsilon

	return math.Log(numerator / denominator)
}

// computeStatistics computes and caches index statistics
func (idx *Index) computeStatistics() {
	if idx.statsComputed {
		return
	}

	idx.totalDocuments = len(idx.docIndex)
	if idx.totalDocuments == 0 {
		idx.avgDocLength = 0
		idx.statsComputed = true
		return
	}

	// Calculate average document length
	totalTerms := 0
	for _, doc := range idx.docIndex {
		totalTerms += doc.TotalTerms
	}
	idx.avgDocLength = float64(totalTerms) / float64(idx.totalDocuments)

	// Precompute IDF values for all terms
	for _, termEntry := range idx.termIndex {
		termEntry.IDF = idx.calculateIDF(termEntry.DocCount)
	}

	idx.statsComputed = true
}

// GetTermStats returns statistics for a specific term
func (idx *Index) GetTermStats(term string) (docCount, totalFreq int) {
	if termPos, exists := idx.termMap[term]; exists {
		termEntry := idx.termIndex[termPos]
		docCount = termEntry.DocCount
		for _, freq := range termEntry.TermCounts {
			totalFreq += freq
		}
	}
	return
}

// GetDocumentTermFreq returns the frequency of a term in a specific document
func (idx *Index) GetDocumentTermFreq(docID, term string) int {
	docPos, exists := idx.docMap[docID]
	if !exists {
		return 0
	}

	termPos, exists := idx.termMap[term]
	if !exists {
		return 0
	}

	termEntry := idx.termIndex[termPos]
	for i, docIDInTerm := range termEntry.DocIDs {
		if docIDInTerm == docPos {
			return termEntry.TermCounts[i]
		}
	}

	return 0
}

// GetTermIDF returns the IDF value for a specific term
func (idx *Index) GetTermIDF(term string) float64 {
	idx.computeStatistics()

	if termPos, exists := idx.termMap[term]; exists {
		return idx.termIndex[termPos].IDF
	}
	return 0.0
}

// GetIndexStats returns index statistics
func (idx *Index) GetIndexStats() (totalDocs, totalTerms, avgLength float64) {
	idx.computeStatistics()
	return float64(idx.totalDocuments), float64(len(idx.termIndex)), idx.avgDocLength
}

// GetDocumentCount returns the total number of documents
func (idx *Index) GetDocumentCount() int {
	return len(idx.docIndex)
}

// GetTermCount returns the total number of unique terms
func (idx *Index) GetTermCount() int {
	return len(idx.termIndex)
}

// GetAverageDocumentLength returns the average document length
func (idx *Index) GetAverageDocumentLength() float64 {
	idx.computeStatistics()
	return idx.avgDocLength
}

// Clear removes all documents from the index
func (idx *Index) Clear() {
	idx.termIndex = idx.termIndex[:0]
	idx.docIndex = idx.docIndex[:0]
	idx.termMap = make(map[string]int)
	idx.docMap = make(map[string]int)
	idx.totalDocuments = 0
	idx.avgDocLength = 0
	idx.statsComputed = false
}

// IsEmpty returns true if the index contains no documents
func (idx *Index) IsEmpty() bool {
	return len(idx.docIndex) == 0
}

// Tokenize implements the Tokenizer interface for DefaultTokenizer
func (dt *DefaultTokenizer) Tokenize(text string) []string {
	// Convert to lowercase and split by whitespace
	text = strings.ToLower(text)
	fields := strings.Fields(text)

	// Filter out empty tokens and apply basic cleaning
	tokens := make([]string, 0, len(fields))
	for _, field := range fields {
		// Remove punctuation from beginning and end
		field = strings.TrimFunc(field, func(r rune) bool {
			return !unicode.IsLetter(r) && !unicode.IsNumber(r)
		})

		if len(field) > 0 {
			tokens = append(tokens, field)
		}
	}

	return tokens
}

// SmartTokenizer implements intelligent tokenization with selective stopword removal
// and compound word support for technical terms, medical conditions, and product names
type SmartTokenizer struct {
	language      string
	compoundWords map[string]bool // Set of compound words to preserve as single tokens
}

// essentialStopwords contains only the most common function words that rarely
// carry meaningful semantic content for search purposes
var essentialStopwords = map[string]bool{
	// Articles
	"a": true, "an": true, "the": true,
	// Basic conjunctions
	"and": true, "or": true, "but": true, "nor": true, "yet": true, "so": true,
	// Basic prepositions (only the most common ones)
	"of": true, "in": true, "to": true, "for": true, "with": true, "by": true, "over": true,
	// Basic pronouns
	"it": true, "its": true, "this": true, "that": true, "these": true, "those": true,
	"i": true, "you": true, "he": true, "she": true, "we": true, "they": true,
	// Basic auxiliary verbs
	"is": true, "are": true, "was": true, "were": true, "be": true, "been": true, "being": true,
	"have": true, "has": true, "had": true, "do": true, "does": true, "did": true,
	"will": true, "would": true, "could": true, "should": true, "may": true, "might": true,
	// Question words
	"how": true, "what": true, "when": true, "where": true, "why": true, "who": true,
	// Basic determiners
	"all": true, "any": true, "each": true, "every": true, "no": true, "some": true,
	// Basic adverbs
	"very": true, "too": true, "as": true, "just": true, "only": true,
}

// NewSmartTokenizer creates a new SmartTokenizer for the specified language
// Currently supports "en" (English) with more languages to be added
func NewSmartTokenizer(language string) *SmartTokenizer {
	return &SmartTokenizer{
		language:      language,
		compoundWords: make(map[string]bool),
	}
}

// NewSmartTokenizerWithCompounds creates a new SmartTokenizer with custom compound words
func NewSmartTokenizerWithCompounds(language string, compoundWords []string) *SmartTokenizer {
	tokenizer := &SmartTokenizer{
		language:      language,
		compoundWords: make(map[string]bool),
	}

	// Add compound words to the set
	for _, compound := range compoundWords {
		tokenizer.compoundWords[strings.ToLower(compound)] = true
	}

	return tokenizer
}

// NewEnglishSmartTokenizer creates a SmartTokenizer for English text
func NewEnglishSmartTokenizer() *SmartTokenizer {
	return NewSmartTokenizer("en")
}

// NewEnglishSmartTokenizerWithCompounds creates an English SmartTokenizer with custom compound words
func NewEnglishSmartTokenizerWithCompounds(compoundWords []string) *SmartTokenizer {
	return NewSmartTokenizerWithCompounds("en", compoundWords)
}

// AddCompoundWord adds a single compound word to the tokenizer
func (st *SmartTokenizer) AddCompoundWord(compound string) {
	st.compoundWords[strings.ToLower(compound)] = true
}

// AddCompoundWords adds multiple compound words to the tokenizer
func (st *SmartTokenizer) AddCompoundWords(compounds []string) {
	for _, compound := range compounds {
		st.compoundWords[strings.ToLower(compound)] = true
	}
}

// RemoveCompoundWord removes a compound word from the tokenizer
func (st *SmartTokenizer) RemoveCompoundWord(compound string) {
	delete(st.compoundWords, strings.ToLower(compound))
}

// GetCompoundWords returns a copy of the current compound words
func (st *SmartTokenizer) GetCompoundWords() []string {
	compounds := make([]string, 0, len(st.compoundWords))
	for compound := range st.compoundWords {
		compounds = append(compounds, compound)
	}
	return compounds
}

// HasCompoundWord checks if a word is a compound word
func (st *SmartTokenizer) HasCompoundWord(word string) bool {
	return st.compoundWords[strings.ToLower(word)]
}

// GetLanguage returns the current language setting of the tokenizer
func (st *SmartTokenizer) GetLanguage() string {
	return st.language
}

// Tokenize implements the Tokenizer interface for SmartTokenizer
func (st *SmartTokenizer) Tokenize(text string) []string {
	// Convert to lowercase first
	text = strings.ToLower(text)

	// Split by whitespace first
	fields := strings.Fields(text)

	// Filter out stopwords and apply cleaning
	tokens := make([]string, 0, len(fields)*3) // Pre-allocate for compound + individual + split tokens
	i := 0

	for i < len(fields) {
		field := fields[i]

		// Split field on punctuation to handle URLs, emails, JSON, etc.
		subTokens := st.splitOnPunctuation(field)

		// Try to find compound words starting from this position
		compoundFound := false
		for compoundLength := 3; compoundLength >= 1; compoundLength-- {
			if i+compoundLength-1 < len(fields) {
				// Build potential compound word from cleaned fields
				potentialCompound := make([]string, compoundLength)
				for j := 0; j < compoundLength; j++ {
					cleaned := strings.TrimFunc(fields[i+j], func(r rune) bool {
						return !unicode.IsLetter(r) && !unicode.IsNumber(r)
					})
					potentialCompound[j] = cleaned
				}

				// Join the potential compound
				compound := strings.Join(potentialCompound, " ")

				// Check if it's a known compound word
				if st.compoundWords[compound] {
					// Add the compound token
					tokens = append(tokens, compound)

					// Also add individual components (if they're not stopwords)
					for j := 0; j < compoundLength; j++ {
						component := potentialCompound[j]
						if len(component) > 0 && !essentialStopwords[component] {
							tokens = append(tokens, component)
						}
					}

					i += compoundLength
					compoundFound = true
					break
				}
			}
		}

		// If no compound word was found, process the sub-tokens
		if !compoundFound {
			for _, subToken := range subTokens {
				// Filter out very short tokens and stopwords
				if len(subToken) > 0 && !essentialStopwords[subToken] {
					tokens = append(tokens, subToken)
				}
			}
			i++
		}
	}

	return tokens
}

// splitOnPunctuation splits a field on common punctuation marks
func (st *SmartTokenizer) splitOnPunctuation(field string) []string {
	// Define punctuation characters that should always split (structural punctuation)
	structuralPunctuation := "{}[]()\"':;!?@#$%^&*+=|\\/<>~`"

	// Check if this looks like a contraction, possessive, or name with apostrophe
	if st.isLikelyContraction(field) {
		// Don't split - return the field as-is (will be cleaned by TrimFunc later)
		return []string{field}
	}

	var result []string
	var currentToken strings.Builder

	for _, char := range field {
		if strings.ContainsRune(structuralPunctuation, char) {
			// If we have accumulated characters, add them as a token
			if currentToken.Len() > 0 {
				token := currentToken.String()
				// Clean the token of any remaining punctuation at edges
				token = strings.TrimFunc(token, func(r rune) bool {
					return !unicode.IsLetter(r) && !unicode.IsNumber(r) && r != '.'
				})
				if len(token) > 0 {
					result = append(result, token)
				}
				currentToken.Reset()
			}
			// Note: We don't add the punctuation character itself as a token
		} else {
			currentToken.WriteRune(char)
		}
	}

	// Add any remaining characters as the final token
	if currentToken.Len() > 0 {
		token := currentToken.String()
		// Clean the token of any remaining punctuation at edges (but preserve dots for decimals)
		token = strings.TrimFunc(token, func(r rune) bool {
			return !unicode.IsLetter(r) && !unicode.IsNumber(r) && r != '.'
		})
		if len(token) > 0 {
			result = append(result, token)
		}
	}

	// Post-process: split any remaining tokens that contain dots (like "example.com")
	var finalResult []string
	for _, token := range result {
		if strings.Contains(token, ".") && !st.isLikelyDecimal(token) {
			// Split on dots for domain names, but preserve decimal numbers
			parts := strings.Split(token, ".")
			for _, part := range parts {
				cleanPart := strings.TrimFunc(part, func(r rune) bool {
					return !unicode.IsLetter(r) && !unicode.IsNumber(r)
				})
				if len(cleanPart) > 0 {
					finalResult = append(finalResult, cleanPart)
				}
			}
		} else {
			finalResult = append(finalResult, token)
		}
	}

	// Post-process: merge adjacent single letters that were split by apostrophes
	finalResult = st.mergeAdjacentLetters(finalResult)

	return finalResult
}

// mergeAdjacentLetters merges adjacent single letters that were likely split by apostrophes
func (st *SmartTokenizer) mergeAdjacentLetters(tokens []string) []string {
	if len(tokens) < 2 {
		return tokens
	}

	var result []string
	i := 0

	for i < len(tokens) {
		if i < len(tokens)-1 && len(tokens[i]) == 1 && len(tokens[i+1]) > 1 {
			// Single letter followed by longer token - likely split by apostrophe
			// Merge them: "d" + "angelo" -> "dangelo"
			merged := tokens[i] + tokens[i+1]
			result = append(result, merged)
			i += 2
		} else if i < len(tokens)-1 && len(tokens[i]) > 1 && len(tokens[i+1]) == 1 {
			// Longer token followed by single letter - likely split by apostrophe
			// Merge them: "mary" + "s" -> "marys"
			merged := tokens[i] + tokens[i+1]
			result = append(result, merged)
			i += 2
		} else {
			// No merging needed
			result = append(result, tokens[i])
			i++
		}
	}

	return result
}

// isLikelyDecimal checks if a token looks like a decimal number
func (st *SmartTokenizer) isLikelyDecimal(token string) bool {
	// Simple heuristic: if it contains exactly one dot and the rest are digits
	dotCount := strings.Count(token, ".")
	if dotCount != 1 {
		return false
	}

	// Check if removing the dot leaves only digits
	withoutDot := strings.ReplaceAll(token, ".", "")
	for _, char := range withoutDot {
		if !unicode.IsDigit(char) {
			return false
		}
	}

	return len(withoutDot) > 0
}

// isLikelyContraction checks if a field looks like it contains a contraction or possessive
func (st *SmartTokenizer) isLikelyContraction(field string) bool {
	// Check for common contraction patterns that should be preserved as single tokens
	contractionPatterns := []string{
		"n't", // don't, can't, won't, etc.
		"'re", // you're, they're, etc.
		"'ve", // I've, you've, etc.
		"'ll", // I'll, you'll, etc.
		"'d",  // I'd, you'd, etc.
		"'m",  // I'm
	}

	for _, pattern := range contractionPatterns {
		if strings.Contains(field, pattern) {
			return true
		}
	}

	// For possessives and names with apostrophes, we want to split them
	// but preserve the meaning, so return false to allow splitting
	return false
}

// generateBenchmarkData generates synthetic document data for benchmarking
func generateBenchmarkData(numDocs int, avgLength int) []string {
	documents := make([]string, numDocs)
	for i := 0; i < numDocs; i++ {
		// Generate a simple document with random content
		docLength := avgLength + (i % 20) - 10 // Vary length slightly
		if docLength < 5 {
			docLength = 5
		}

		words := make([]string, docLength)
		for j := 0; j < docLength; j++ {
			words[j] = fmt.Sprintf("word%d", (i+j)%100)
		}

		documents[i] = strings.Join(words, " ")
	}
	return documents
}

// Error definitions
var ErrCapacityExceeded = errors.New("index capacity exceeded")

// SearchOptimized performs a BM25 search with optimized top-k selection
// This method is designed for maximum performance when you only need top-k results
func (idx *Index) SearchOptimized(query string, tokenizer Tokenizer, limit int) []SearchResult {
	// Ensure statistics are computed
	idx.computeStatistics()

	queryTerms := tokenizer.Tokenize(query)

	// Early termination for empty queries
	if len(queryTerms) == 0 {
		return []SearchResult{}
	}

	// Use heap-based top-k selection for better performance
	if limit > 0 {
		return idx.searchWithHeapOptimized(queryTerms, limit)
	}

	// Fall back to regular search for unlimited results
	return idx.Search(query, tokenizer, 0)
}

// searchWithHeapOptimized performs search using heap-based top-k selection with early termination
func (idx *Index) searchWithHeapOptimized(queryTerms []string, k int) []SearchResult {
	h := &SearchResultHeap{}
	heap.Init(h)

	// Get score map from pool
	docScores := idx.scorePool.Get().(map[int]float64)
	defer func() {
		// Clear and return to pool
		for k := range docScores {
			delete(docScores, k)
		}
		idx.scorePool.Put(docScores)
	}()

	// Process terms in order of potential impact (higher IDF first)
	termEntries := make([]*TermEntry, 0, len(queryTerms))
	for _, term := range queryTerms {
		if termPos, exists := idx.termMap[term]; exists {
			termEntries = append(termEntries, idx.termIndex[termPos])
		}
	}

	// Sort terms by IDF (descending) to process most impactful terms first
	sort.Slice(termEntries, func(i, j int) bool {
		return termEntries[i].IDF > termEntries[j].IDF
	})

	// Track minimum score threshold for early termination
	minScoreThreshold := 0.0
	documentsProcessed := 0

	// Process each term and maintain top-k results
	for _, termEntry := range termEntries {
		idf := termEntry.IDF

		// Skip terms with very low IDF (likely stopwords or very common terms)
		if idf < idx.params.Epsilon {
			continue
		}

		// Process documents containing this term
		for i, docPos := range termEntry.DocIDs {
			if docPos >= len(idx.docIndex) {
				continue
			}

			termFreq := termEntry.TermCounts[i]
			docScore := idx.calculateBM25Score(termFreq, docPos, idf)

			// Early termination: skip documents below threshold if we have enough results
			if h.Len() >= k && docScore < minScoreThreshold {
				continue
			}

			// Add to heap if we have space or if score is better than current minimum
			if h.Len() < k {
				heap.Push(h, SearchResult{
					DocID: idx.docIndex[docPos].DocID,
					Score: docScore,
				})
			} else if docScore > (*h)[0].Score {
				// Replace smallest score with larger one
				heap.Pop(h)
				heap.Push(h, SearchResult{
					DocID: idx.docIndex[docPos].DocID,
					Score: docScore,
				})
			}

			// Update minimum score threshold for early termination
			if h.Len() >= k {
				minScoreThreshold = (*h)[0].Score
			}

			documentsProcessed++
		}

		// Early termination: if we have enough high-scoring results and processed many documents
		if h.Len() >= k && documentsProcessed > k*10 && minScoreThreshold > idx.params.Epsilon {
			break
		}
	}

	// Extract results in descending order
	results := make([]SearchResult, h.Len())
	for i := len(results) - 1; i >= 0; i-- {
		results[i] = heap.Pop(h).(SearchResult)
	}

	return results
}

// searchWithHeap performs search using heap-based top-k selection
func (idx *Index) searchWithHeap(queryTerms []string, k int) []SearchResult {
	h := &SearchResultHeap{}
	heap.Init(h)

	// Process each term and maintain top-k results
	for _, term := range queryTerms {
		if termPos, exists := idx.termMap[term]; exists {
			termEntry := idx.termIndex[termPos]
			idf := termEntry.IDF

			// Process documents containing this term
			for i, docPos := range termEntry.DocIDs {
				if docPos >= len(idx.docIndex) {
					continue
				}

				termFreq := termEntry.TermCounts[i]
				docScore := idx.calculateBM25Score(termFreq, docPos, idf)

				// Add to heap if we have space or if score is better than current minimum
				if h.Len() < k {
					heap.Push(h, SearchResult{
						DocID: idx.docIndex[docPos].DocID,
						Score: docScore,
					})
				} else if docScore > (*h)[0].Score {
					// Replace smallest score with larger one
					heap.Pop(h)
					heap.Push(h, SearchResult{
						DocID: idx.docIndex[docPos].DocID,
						Score: docScore,
					})
				}
			}
		}
	}

	// Extract results in descending order
	results := make([]SearchResult, h.Len())
	for i := len(results) - 1; i >= 0; i-- {
		results[i] = heap.Pop(h).(SearchResult)
	}

	return results
}

// SearchWithThreshold performs a BM25 search with score thresholding for better performance
func (idx *Index) SearchWithThreshold(query string, tokenizer Tokenizer, limit int, minScore float64) []SearchResult {
	// Ensure statistics are computed
	idx.computeStatistics()

	queryTerms := tokenizer.Tokenize(query)

	// Early termination for empty queries
	if len(queryTerms) == 0 {
		return []SearchResult{}
	}

	// Get score map from pool
	docScores := idx.scorePool.Get().(map[int]float64)
	defer func() {
		// Clear and return to pool
		for k := range docScores {
			delete(docScores, k)
		}
		idx.scorePool.Put(docScores)
	}()

	// Calculate scores for each document with threshold filtering
	for _, term := range queryTerms {
		if termPos, exists := idx.termMap[term]; exists {
			termEntry := idx.termIndex[termPos]
			idf := termEntry.IDF

			// Skip terms with very low IDF
			if idf < idx.params.Epsilon {
				continue
			}

			// Calculate scores for documents containing this term
			for i, docPos := range termEntry.DocIDs {
				termFreq := termEntry.TermCounts[i]
				docScore := idx.calculateBM25Score(termFreq, docPos, idf)

				// Only add scores above threshold
				if docScore >= minScore {
					docScores[docPos] += docScore
				}
			}
		}
	}

	// Use heap-based top-k selection for better performance
	if limit > 0 && limit < len(docScores) {
		return idx.selectTopK(docScores, limit)
	}

	// Convert all scores to results and sort (for small result sets)
	results := make([]SearchResult, 0, len(docScores))
	for docPos, score := range docScores {
		if docPos < len(idx.docIndex) && score >= minScore {
			results = append(results, SearchResult{
				DocID: idx.docIndex[docPos].DocID,
				Score: score,
			})
		}
	}

	// Sort by score (descending)
	sort.Slice(results, func(i, j int) bool {
		return results[i].Score > results[j].Score
	})

	return results
}

// BatchSearch performs multiple searches efficiently
func (idx *Index) BatchSearch(queries []string, tokenizer Tokenizer, limit int) []BatchSearchResult {
	results := make([]BatchSearchResult, len(queries))

	// Process queries in parallel for better performance
	var wg sync.WaitGroup
	semaphore := make(chan struct{}, 4) // Limit concurrent goroutines

	for i, query := range queries {
		wg.Add(1)
		go func(resultIdx int, q string) {
			defer wg.Done()

			// Acquire semaphore
			semaphore <- struct{}{}
			defer func() { <-semaphore }()

			// Check cache first if enabled
			if idx.cacheEnabled && idx.searchCache != nil {
				if cached, exists := idx.searchCache.Get(q); exists {
					results[resultIdx] = BatchSearchResult{
						Query:   q,
						Results: cached,
					}
					return
				}
			}

			// Perform search
			searchResults := idx.SearchOptimized(q, tokenizer, limit)

			// Cache results if enabled
			if idx.cacheEnabled && idx.searchCache != nil {
				idx.searchCache.Set(q, searchResults)
			}

			results[resultIdx] = BatchSearchResult{
				Query:   q,
				Results: searchResults,
			}
		}(i, query)
	}

	wg.Wait()
	return results
}

// SearchWithCache performs a search with optional result caching
func (idx *Index) SearchWithCache(query string, tokenizer Tokenizer, limit int) []SearchResult {
	// Check cache first if enabled
	if idx.cacheEnabled && idx.searchCache != nil {
		if cached, exists := idx.searchCache.Get(query); exists {
			// Return cached results up to the requested limit
			if limit > 0 && len(cached) > limit {
				return cached[:limit]
			}
			return cached
		}
	}

	// Perform search (use standard Search to avoid aggressive term skipping)
	results := idx.Search(query, tokenizer, limit)

	// Cache results if enabled
	if idx.cacheEnabled && idx.searchCache != nil {
		idx.searchCache.Set(query, results)
	}

	return results
}

// GetTermImpact returns the impact score of a term based on its IDF and frequency
func (idx *Index) GetTermImpact(term string) float64 {
	idx.computeStatistics()

	if termPos, exists := idx.termMap[term]; exists {
		termEntry := idx.termIndex[termPos]
		// Impact is based on IDF and how many documents contain the term
		return termEntry.IDF * float64(termEntry.DocCount)
	}
	return 0.0
}

// GetQueryTermsImpact returns terms sorted by their potential impact on search results
func (idx *Index) GetQueryTermsImpact(query string, tokenizer Tokenizer) []string {
	queryTerms := tokenizer.Tokenize(query)

	// Sort terms by impact (IDF * doc frequency)
	type termImpact struct {
		term   string
		impact float64
	}

	impacts := make([]termImpact, 0, len(queryTerms))
	for _, term := range queryTerms {
		impact := idx.GetTermImpact(term)
		if impact > 0 {
			impacts = append(impacts, termImpact{term, impact})
		}
	}

	// Sort by impact (descending)
	sort.Slice(impacts, func(i, j int) bool {
		return impacts[i].impact > impacts[j].impact
	})

	// Extract sorted terms
	result := make([]string, len(impacts))
	for i, ti := range impacts {
		result[i] = ti.term
	}

	return result
}

// VectorizedSearch performs search with vectorized scoring for better performance
func (idx *Index) VectorizedSearch(query string, tokenizer Tokenizer, limit int) []SearchResult {
	// Ensure statistics are computed
	idx.computeStatistics()

	queryTerms := tokenizer.Tokenize(query)

	// Early termination for empty queries
	if len(queryTerms) == 0 {
		return []SearchResult{}
	}

	// Get score map from pool
	docScores := idx.scorePool.Get().(map[int]float64)
	defer func() {
		// Clear and return to pool
		for k := range docScores {
			delete(docScores, k)
		}
		idx.scorePool.Put(docScores)
	}()

	// Pre-allocate slices for vectorized operations
	termEntries := make([]*TermEntry, 0, len(queryTerms))
	termIDFs := make([]float64, 0, len(queryTerms))

	// Collect all term information upfront
	for _, term := range queryTerms {
		if termPos, exists := idx.termMap[term]; exists {
			termEntry := idx.termIndex[termPos]
			termEntries = append(termEntries, termEntry)
			termIDFs = append(termIDFs, termEntry.IDF)
		}
	}

	// Early termination if no valid terms
	if len(termEntries) == 0 {
		return []SearchResult{}
	}

	// Vectorized scoring: process all terms simultaneously for each document
	docSet := make(map[int]bool)

	// First pass: collect all relevant documents
	for _, termEntry := range termEntries {
		for _, docPos := range termEntry.DocIDs {
			docSet[docPos] = true
		}
	}

	// Second pass: vectorized scoring
	for docPos := range docSet {
		if docPos >= len(idx.docIndex) {
			continue
		}

		docLength := float64(idx.docIndex[docPos].TotalTerms)
		normalizedLength := docLength / idx.avgDocLength

		// Calculate combined score for all terms in this document
		totalScore := 0.0
		for i, termEntry := range termEntries {
			idf := termIDFs[i]

			// Find term frequency in this document
			termFreq := 0
			for j, docID := range termEntry.DocIDs {
				if docID == docPos {
					termFreq = termEntry.TermCounts[j]
					break
				}
			}

			if termFreq > 0 {
				// Vectorized BM25 calculation
				numerator := float64(termFreq) * (idx.params.K1 + 1.0)
				denominator := float64(termFreq) + idx.params.K1*(1.0-idx.params.B+idx.params.B*normalizedLength)
				totalScore += idf * numerator / denominator
			}
		}

		docScores[docPos] = totalScore
	}

	// Use heap-based top-k selection for better performance
	if limit > 0 && limit < len(docScores) {
		return idx.selectTopK(docScores, limit)
	}

	// Convert all scores to results and sort (for small result sets)
	results := make([]SearchResult, 0, len(docScores))
	for docPos, score := range docScores {
		if docPos < len(idx.docIndex) {
			results = append(results, SearchResult{
				DocID: idx.docIndex[docPos].DocID,
				Score: score,
			})
		}
	}

	// Sort by score (descending)
	sort.Slice(results, func(i, j int) bool {
		return results[i].Score > results[j].Score
	})

	return results
}

// BulkAddDocuments efficiently adds multiple documents with optimized memory usage
func (idx *Index) BulkAddDocuments(documents []Document, tokenizer Tokenizer) error {
	if len(idx.docIndex)+len(documents) > idx.docCapacity {
		return ErrCapacityExceeded
	}

	// Pre-allocate memory for better performance
	idx.termIndex = append(idx.termIndex, make([]*TermEntry, 0, len(documents)*10)...)
	idx.docIndex = append(idx.docIndex, make([]*DocumentEntry, 0, len(documents))...)

	// Process documents in batches for better memory locality
	batchSize := 100
	for i := 0; i < len(documents); i += batchSize {
		end := i + batchSize
		if end > len(documents) {
			end = len(documents)
		}

		batch := documents[i:end]
		if err := idx.processDocumentBatch(batch, tokenizer); err != nil {
			return err
		}
	}

	// Mark statistics as needing recomputation
	idx.statsComputed = false
	return nil
}

// processDocumentBatch processes a batch of documents efficiently
func (idx *Index) processDocumentBatch(documents []Document, tokenizer Tokenizer) error {
	// Pre-allocate term frequency maps for the batch
	batchTermFreqs := make([]map[string]int, len(documents))
	for i := range batchTermFreqs {
		batchTermFreqs[i] = make(map[string]int)
	}

	// Tokenize all documents in the batch
	for i, doc := range documents {
		terms := tokenizer.Tokenize(doc.Content)
		for _, term := range terms {
			batchTermFreqs[i][term]++
		}
	}

	// Add documents to index
	for i, doc := range documents {
		docEntry := &DocumentEntry{
			DocID:       doc.ID,
			TotalTerms:  0,
			UniqueTerms: 0,
			Terms:       make([]string, 0, len(batchTermFreqs[i])),
			TermFreqs:   make([]int, 0, len(batchTermFreqs[i])),
		}

		// Build term arrays
		for term, freq := range batchTermFreqs[i] {
			docEntry.Terms = append(docEntry.Terms, term)
			docEntry.TermFreqs = append(docEntry.TermFreqs, freq)
			docEntry.TotalTerms += freq
		}
		docEntry.UniqueTerms = len(docEntry.Terms)

		// Add document to index
		docPos := len(idx.docIndex)
		idx.docIndex = append(idx.docIndex, docEntry)
		idx.docMap[doc.ID] = docPos

		// Update term index
		for j, term := range docEntry.Terms {
			freq := docEntry.TermFreqs[j]

			// Find or create term entry
			termPos, exists := idx.termMap[term]
			if !exists {
				termEntry := &TermEntry{
					Term:       term,
					DocCount:   0,
					DocIDs:     make([]int, 0, 10),
					TermCounts: make([]int, 0, 10),
				}
				termPos = len(idx.termIndex)
				idx.termIndex = append(idx.termIndex, termEntry)
				idx.termMap[term] = termPos
			}

			// Update term entry
			termEntry := idx.termIndex[termPos]
			termEntry.DocCount++
			termEntry.DocIDs = append(termEntry.DocIDs, docPos)
			termEntry.TermCounts = append(termEntry.TermCounts, freq)
		}
	}

	return nil
}

// GetPerformanceStats returns performance-related statistics
func (idx *Index) GetPerformanceStats() map[string]interface{} {
	idx.computeStatistics()

	stats := make(map[string]interface{})
	stats["total_documents"] = idx.totalDocuments
	stats["total_terms"] = len(idx.termIndex)
	stats["average_document_length"] = idx.avgDocLength
	stats["memory_usage_mb"] = idx.estimateMemoryUsage()
	stats["cache_enabled"] = idx.cacheEnabled
	if idx.searchCache != nil {
		stats["cache_size"] = len(idx.searchCache.cache)
		stats["cache_max_size"] = idx.searchCache.maxSize
	}

	return stats
}

// estimateMemoryUsage estimates the memory usage of the index in bytes
func (idx *Index) estimateMemoryUsage() int64 {
	var total int64

	// Estimate memory for term index
	for _, term := range idx.termIndex {
		total += int64(len(term.Term)) + 8 + 8 + int64(len(term.DocIDs)*8) + int64(len(term.TermCounts)*8)
	}

	// Estimate memory for document index
	for _, doc := range idx.docIndex {
		total += int64(len(doc.DocID)) + 8 + 8 + int64(len(doc.Terms)*16) + int64(len(doc.TermFreqs)*8)
	}

	// Estimate memory for maps
	total += int64(len(idx.termMap) * 32) // Approximate size for string->int mapping
	total += int64(len(idx.docMap) * 32)  // Approximate size for string->int mapping

	return total / 1024 / 1024 // Convert to MB
}

// TermIDFIterator creates a new iterator for iterating over term-IDF pairs
func (idx *Index) TermIDFIterator() *TermIDFIterator {
	// Ensure statistics are computed so IDF values are up to date
	idx.computeStatistics()

	return &TermIDFIterator{
		index:    idx,
		position: -1,
		current:  nil,
	}
}

// Next advances the iterator to the next term-IDF pair
// Returns true if a next pair is available, false if iteration is complete
func (it *TermIDFIterator) Next() bool {
	it.position++

	if it.position >= len(it.index.termIndex) {
		it.current = nil
		return false
	}

	termEntry := it.index.termIndex[it.position]
	it.current = &TermIDFPair{
		Term:     termEntry.Term,
		IDF:      termEntry.IDF,
		DocCount: termEntry.DocCount,
	}

	return true
}

// Current returns the current term-IDF pair
// Returns nil if the iterator is not positioned on a valid pair
func (it *TermIDFIterator) Current() *TermIDFPair {
	return it.current
}

// Reset resets the iterator to the beginning
func (it *TermIDFIterator) Reset() {
	it.position = -1
	it.current = nil
}

// HasNext returns true if there are more term-IDF pairs to iterate over
func (it *TermIDFIterator) HasNext() bool {
	return it.position+1 < len(it.index.termIndex)
}

// Count returns the total number of terms available for iteration
func (it *TermIDFIterator) Count() int {
	return len(it.index.termIndex)
}

// GetTermIDFByIndex returns the term-IDF pair at a specific index
// Returns nil if the index is out of bounds
func (idx *Index) GetTermIDFByIndex(index int) *TermIDFPair {
	// Ensure statistics are computed
	idx.computeStatistics()

	if index < 0 || index >= len(idx.termIndex) {
		return nil
	}

	termEntry := idx.termIndex[index]
	return &TermIDFPair{
		Term:     termEntry.Term,
		IDF:      termEntry.IDF,
		DocCount: termEntry.DocCount,
	}
}

// GetAllTermIDFs returns all term-IDF pairs as a slice
// This method returns the entire vector of terms and their IDF values
func (idx *Index) GetAllTermIDFs() []TermIDFPair {
	// Ensure statistics are computed
	idx.computeStatistics()

	pairs := make([]TermIDFPair, len(idx.termIndex))
	for i, termEntry := range idx.termIndex {
		pairs[i] = TermIDFPair{
			Term:     termEntry.Term,
			IDF:      termEntry.IDF,
			DocCount: termEntry.DocCount,
		}
	}

	return pairs
}

// GetTermIDFsSorted returns all term-IDF pairs sorted by the specified criteria
func (idx *Index) GetTermIDFsSorted(sortBy string) []TermIDFPair {
	pairs := idx.GetAllTermIDFs()

	switch sortBy {
	case "term":
		sort.Slice(pairs, func(i, j int) bool {
			return pairs[i].Term < pairs[j].Term
		})
	case "idf":
		sort.Slice(pairs, func(i, j int) bool {
			return pairs[i].IDF > pairs[j].IDF // Descending order (higher IDF first)
		})
	case "doccount":
		sort.Slice(pairs, func(i, j int) bool {
			return pairs[i].DocCount > pairs[j].DocCount // Descending order (more frequent terms first)
		})
	case "rarity":
		sort.Slice(pairs, func(i, j int) bool {
			return pairs[i].DocCount < pairs[j].DocCount // Ascending order (rarer terms first)
		})
	}

	return pairs
}

// TermMatch represents a term match found in a document
type TermMatch struct {
	Term      string
	Frequency int
	Position  int // Position in the document (approximate)
}

// GetMatches returns term matches found in a specific document for the given tokens
func (idx *Index) GetMatches(tokens []string, docID string) []TermMatch {
	// Find the document position
	docPos, exists := idx.docMap[docID]
	if !exists {
		return []TermMatch{}
	}

	// Get the document entry
	docEntry := idx.docIndex[docPos]
	if docEntry == nil {
		return []TermMatch{}
	}

	// Create a map for fast term lookup in the document
	docTermMap := make(map[string]int)
	for i, term := range docEntry.Terms {
		docTermMap[term] = docEntry.TermFreqs[i]
	}

	// Find matches for the given tokens
	var matches []TermMatch
	for _, token := range tokens {
		if freq, exists := docTermMap[token]; exists {
			// Find the position of this term in the document
			position := -1
			for i, term := range docEntry.Terms {
				if term == token {
					position = i
					break
				}
			}

			matches = append(matches, TermMatch{
				Term:      token,
				Frequency: freq,
				Position:  position,
			})
		}
	}

	return matches
}
