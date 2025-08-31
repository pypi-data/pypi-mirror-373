package main

import (
	"C"
	"encoding/json"
	"sync"
)

var (
	indexes = make(map[int64]*Index)
	tokenizers = make(map[int64]*SmartTokenizer)
	nextHandle int64 = 1
	handleMutex sync.Mutex
)

//export HelloBM25
func HelloBM25() *C.char {
	return C.CString("Hello from Go BM25!")
}

//export NewBM25Index
func NewBM25Index(docCapacity, termCapacity C.int) C.longlong {
	idx := NewIndex(int(docCapacity), int(termCapacity))
	
	handleMutex.Lock()
	handle := nextHandle
	nextHandle++
	indexes[handle] = idx
	handleMutex.Unlock()
	
	return C.longlong(handle)
}

//export AddDocument
func AddDocument(handle C.longlong, docID, content *C.char) C.int {
	handleMutex.Lock()
	idx, exists := indexes[int64(handle)]
	handleMutex.Unlock()
	
	if !exists {
		return 1
	}
	
	tokenizer := &DefaultTokenizer{}
	err := idx.AddDocument(C.GoString(docID), C.GoString(content), tokenizer)
	if err != nil {
		return 1
	}
	return 0
}

//export Search
func Search(handle C.longlong, query *C.char, limit C.int) *C.char {
	handleMutex.Lock()
	idx, exists := indexes[int64(handle)]
	handleMutex.Unlock()
	
	if !exists {
		return C.CString("[]")
	}
	
	tokenizer := &DefaultTokenizer{}
	results := idx.Search(C.GoString(query), tokenizer, int(limit))
	
	// Convert results to JSON
	jsonData, _ := json.Marshal(results)
	return C.CString(string(jsonData))
}

//export CreateEnglishSmartTokenizer
func CreateEnglishSmartTokenizer() C.longlong {
	tokenizer := NewEnglishSmartTokenizer()
	
	handleMutex.Lock()
	handle := nextHandle
	nextHandle++
	tokenizers[handle] = tokenizer
	handleMutex.Unlock()
	
	return C.longlong(handle)
}

//export CreateSmartTokenizer
func CreateSmartTokenizer(language *C.char) C.longlong {
	tokenizer := NewSmartTokenizer(C.GoString(language))
	
	handleMutex.Lock()
	handle := nextHandle
	nextHandle++
	tokenizers[handle] = tokenizer
	handleMutex.Unlock()
	
	return C.longlong(handle)
}

//export TokenizeText
func TokenizeText(handle C.longlong, text *C.char) *C.char {
	handleMutex.Lock()
	tokenizer, exists := tokenizers[int64(handle)]
	handleMutex.Unlock()
	
	if !exists {
		return C.CString("[]")
	}
	
	tokens := tokenizer.Tokenize(C.GoString(text))
	
	// Convert tokens to JSON
	jsonData, _ := json.Marshal(tokens)
	return C.CString(string(jsonData))
}

//export BatchSearch
func BatchSearch(handle C.longlong, queries *C.char, tokenizerHandle C.longlong, limit C.int) *C.char {
	handleMutex.Lock()
	idx, exists := indexes[int64(handle)]
	handleMutex.Unlock()
	
	if !exists {
		return C.CString("[]")
	}
	
	// Get tokenizer
	handleMutex.Lock()
	tokenizer, tokenizerExists := tokenizers[int64(tokenizerHandle)]
	handleMutex.Unlock()
	
	if !tokenizerExists {
		return C.CString("[]")
	}
	
	// Parse queries JSON
	queriesStr := C.GoString(queries)
	var queryList []string
	if err := json.Unmarshal([]byte(queriesStr), &queryList); err != nil {
		return C.CString("[]")
	}
	
	// Perform batch search
	batchResults := idx.BatchSearch(queryList, tokenizer, int(limit))
	
	// Convert results to JSON
	jsonData, _ := json.Marshal(batchResults)
	return C.CString(string(jsonData))
}

//export GetMatches
func GetMatches(handle C.longlong, tokens *C.char, docID *C.char) *C.char {
	handleMutex.Lock()
	idx, exists := indexes[int64(handle)]
	handleMutex.Unlock()
	
	if !exists {
		return C.CString("[]")
	}
	
	// Parse tokens JSON
	tokensStr := C.GoString(tokens)
	var tokenList []string
	if err := json.Unmarshal([]byte(tokensStr), &tokenList); err != nil {
		return C.CString("[]")
	}
	
	// Get matches
	matches := idx.GetMatches(tokenList, C.GoString(docID))
	
	// Convert matches to JSON
	jsonData, _ := json.Marshal(matches)
	return C.CString(string(jsonData))
}

func main() {}