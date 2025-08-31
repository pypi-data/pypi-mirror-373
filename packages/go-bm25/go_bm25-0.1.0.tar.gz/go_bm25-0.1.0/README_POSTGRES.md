# BM25 PostgreSQL Integration

This document describes the PostgreSQL integration features of the BM25 Go library, which allows you to persist BM25 indexes in a PostgreSQL database for scalable, persistent text search and ranking.

## Features

- **Persistent Storage**: Store BM25 indexes in PostgreSQL for long-term persistence
- **Scalable Architecture**: Handle large document collections that exceed memory limits
- **ACID Transactions**: All operations are wrapped in database transactions for data integrity
- **Automatic Schema Management**: Tables and indexes are created automatically
- **High-Performance Queries**: Leverage PostgreSQL's optimized query execution
- **Flexible Configuration**: Easy connection configuration and management

## Prerequisites

### PostgreSQL Setup

1. **Install PostgreSQL** (version 12 or higher recommended)
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # macOS
   brew install postgresql
   
   # CentOS/RHEL
   sudo yum install postgresql postgresql-server
   ```

2. **Create Database**
   ```bash
   sudo -u postgres createdb bm25
   ```

3. **Install Go Dependencies**
   ```bash
   go mod tidy
   go mod download
   ```

## Quick Start

### Basic Usage

```go
package main

import (
    "fmt"
    "log"
    "github.com/pentney/go-bm25"
)

func main() {
    // Create PostgreSQL configuration
    config := bm25.DefaultPostgresConfig()
    config.Password = "your_password" // Set your actual password
    
    // Create PostgreSQL index
    index, err := bm25.NewPostgresIndex(config)
    if err != nil {
        log.Fatalf("Failed to create index: %v", err)
    }
    defer index.Close()
    
    // Add documents
    tokenizer := &bm25.DefaultTokenizer{}
    err = index.AddDocument("doc1", "The quick brown fox jumps over the lazy dog", tokenizer)
    if err != nil {
        log.Fatalf("Failed to add document: %v", err)
    }
    
    // Search documents
    results, err := index.Search("quick brown fox", tokenizer, 10)
    if err != nil {
        log.Fatalf("Search failed: %v", err)
    }
    
    for i, result := range results {
        fmt.Printf("%d. %s (score: %.4f)\n", i+1, result.DocID, result.Score)
    }
}
```

### Configuration Options

```go
config := bm25.PostgresConfig{
    Host:     "localhost",      // Database host
    Port:     5432,            // Database port
    User:     "postgres",      // Database user
    Password: "secret",        // Database password
    DBName:   "bm25",          // Database name
    SSLMode:  "disable",       // SSL mode (disable, require, verify-ca, verify-full)
}
```

## Database Schema

The PostgreSQL integration automatically creates the following schema:

### Tables

- **`documents`**: Stores document metadata and content
- **`terms`**: Stores unique terms and their global statistics
- **`term_document_freqs`**: Stores term frequencies within documents

### Indexes

- Primary keys and foreign key constraints
- Performance indexes on frequently queried columns
- Composite indexes for efficient joins

### Functions

- **`calculate_bm25_score()`**: Calculate BM25 score for term-document pairs
- **`search_documents_bm25()`**: Search documents by multiple terms
- **`get_term_statistics()`**: Get comprehensive term statistics
- **`get_index_statistics()`**: Get overall index statistics

## API Reference

### Core Methods

#### `NewPostgresIndex(config PostgresConfig) (*PostgresIndex, error)`
Creates a new PostgreSQL-based BM25 index.

#### `AddDocument(docID, content string, tokenizer Tokenizer) error`
Adds a document to the index with automatic term extraction and frequency counting.

#### `Search(query string, tokenizer Tokenizer, limit int) ([]SearchResult, error)`
Searches for documents using BM25 ranking with PostgreSQL-optimized queries.

#### `GetTermStats(term string) (docCount, totalFreq int, err error)`
Retrieves document frequency and total frequency for a specific term.

#### `GetDocumentTermFreq(docID, term string) (int, error)`
Gets the frequency of a term within a specific document.

#### `GetIndexStats() (totalDocs, totalTerms int, avgLength float64, err error)`
Retrieves comprehensive index statistics.

#### `DeleteDocument(docID string) error`
Removes a document and all associated term frequencies from the index.

#### `UpdateDocument(docID, content string, tokenizer Tokenizer) error`
Updates an existing document by deleting and re-adding it with new content.

#### `ListDocuments(limit, offset int) ([]DocumentInfo, error)`
Lists documents with pagination support.

### Document Management

```go
// Add multiple documents
documents := []struct {
    id      string
    content string
}{
    {"doc1", "Content of first document"},
    {"doc2", "Content of second document"},
    {"doc3", "Content of third document"},
}

for _, doc := range documents {
    err := index.AddDocument(doc.id, doc.content, tokenizer)
    if err != nil {
        log.Printf("Failed to add %s: %v", doc.id, err)
    }
}

// Update a document
err = index.UpdateDocument("doc1", "Updated content", tokenizer)

// Delete a document
err = index.DeleteDocument("doc1")

// List documents with pagination
docs, err := index.ListDocuments(10, 0) // First 10 documents
```

## Performance Considerations

### Indexing Performance

- **Batch Operations**: Consider batching document additions for large datasets
- **Transaction Size**: Large transactions may impact performance; monitor transaction duration
- **Connection Pooling**: The library uses a single connection; consider connection pooling for high-concurrency applications

### Search Performance

- **Query Optimization**: PostgreSQL automatically optimizes queries using the created indexes
- **Result Limiting**: Always use reasonable limits on search results
- **Term Frequency**: Queries with rare terms may be slower due to index lookups

### Memory Usage

- **Document Content**: Large document content is stored in the database, reducing memory usage
- **Term Storage**: Only unique terms are stored, with frequency counts
- **Connection Memory**: Each index instance maintains one database connection

## Benchmarking

Run PostgreSQL-specific benchmarks:

```bash
# Install dependencies
make -f Makefile.benchmark deps

# Run PostgreSQL benchmarks only
make -f Makefile.benchmark run_postgres

# Run all benchmarks
make -f Makefile.benchmark run_all
```

### Benchmark Categories

- **`BenchmarkPostgresIndexing`**: Document indexing performance
- **`BenchmarkPostgresSearch`**: Search query performance
- **`BenchmarkPostgresTermStats`**: Term statistics retrieval
- **`BenchmarkPostgresDocumentFreq`**: Document term frequency lookups
- **`BenchmarkPostgresIndexStats`**: Index statistics retrieval
- **`BenchmarkPostgresBulkOperations`**: Bulk document operations

## Example Applications

### Web Search Engine

```go
func handleSearch(w http.ResponseWriter, r *http.Request) {
    query := r.URL.Query().Get("q")
    if query == "" {
        http.Error(w, "Query parameter required", http.StatusBadRequest)
        return
    }
    
    results, err := index.Search(query, tokenizer, 20)
    if err != nil {
        http.Error(w, "Search failed", http.StatusInternalServerError)
        return
    }
    
    // Return JSON results
    json.NewEncoder(w).Encode(results)
}
```

### Document Management System

```go
func addDocument(w http.ResponseWriter, r *http.Request) {
    var doc struct {
        ID      string `json:"id"`
        Content string `json:"content"`
    }
    
    if err := json.NewDecoder(r.Body).Decode(&doc); err != nil {
        http.Error(w, "Invalid JSON", http.StatusBadRequest)
        return
    }
    
    err := index.AddDocument(doc.ID, doc.Content, tokenizer)
    if err != nil {
        http.Error(w, "Failed to add document", http.StatusInternalServerError)
        return
    }
    
    w.WriteHeader(http.StatusCreated)
}
```

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Verify PostgreSQL is running
   - Check connection parameters (host, port, credentials)
   - Ensure database exists

2. **Permission Denied**
   - Verify user has CREATE, INSERT, SELECT, UPDATE, DELETE permissions
   - Check database ownership

3. **Schema Creation Failed**
   - Ensure user has CREATE TABLE permission
   - Check for existing tables with conflicting names

4. **Performance Issues**
   - Monitor database query performance
   - Check index usage with `EXPLAIN ANALYZE`
   - Consider database tuning parameters

### Debug Mode

Enable detailed logging by setting environment variables:

```bash
export PGDEBUG=1
export PGLOGLEVEL=debug
```

## Migration from In-Memory

### Step-by-Step Migration

1. **Backup Existing Data**
   ```go
   // Export existing in-memory index
   oldIndex := bm25.NewIndex(1000, 10000)
   // ... populate with existing data
   
   // Export documents
   for _, doc := range oldIndex.documents {
       // Save document content and metadata
   }
   ```

2. **Create PostgreSQL Index**
   ```go
   config := bm25.DefaultPostgresConfig()
   pgIndex, err := bm25.NewPostgresIndex(config)
   ```

3. **Import Data**
   ```go
   // Re-add documents to PostgreSQL
   for _, doc := range exportedDocs {
       err := pgIndex.AddDocument(doc.ID, doc.Content, tokenizer)
   }
   ```

4. **Verify Migration**
   ```go
   // Compare statistics
   oldStats := oldIndex.GetIndexStats()
   newStats, err := pgIndex.GetIndexStats()
   
   // Verify search results match
   ```

## Best Practices

### Database Design

- **Regular Maintenance**: Run `VACUUM` and `ANALYZE` regularly
- **Monitoring**: Monitor table sizes and query performance
- **Backup Strategy**: Implement regular database backups

### Application Design

- **Connection Management**: Close index connections when done
- **Error Handling**: Always check for errors and implement retry logic
- **Resource Cleanup**: Use `defer index.Close()` for proper cleanup

### Performance Optimization

- **Batch Operations**: Group document operations when possible
- **Query Optimization**: Use appropriate result limits
- **Index Monitoring**: Monitor index usage and performance

## Batch Mode for High-Performance Processing

For applications requiring high-frequency searches on stable indexes, the PostgreSQL integration provides a **Batch Mode** that loads all data into memory for maximum performance.

### When to Use Batch Mode

- **High-frequency searches**: 100+ searches per second
- **Stable indexes**: Data doesn't change frequently
- **Memory availability**: Can accommodate index size in RAM
- **Batch processing**: Need to process many queries quickly

### Performance Characteristics

- **Search Speed**: 10-100x faster than database queries
- **Memory Usage**: ~1-5GB for 200K documents (depending on content length)
- **Initialization**: One-time cost to load data into memory
- **Scalability**: Limited by available RAM, not database performance

### Usage Example

```go
// Create PostgreSQL index
config := bm25.DefaultPostgresConfig()
pgIndex, err := bm25.NewPostgresIndex(config)
if err != nil {
    log.Fatalf("Failed to create index: %v", err)
}
defer pgIndex.Close()

// Create batch mode for high-performance searches
batchMode, err := pgIndex.NewBatchMode()
if err != nil {
    log.Fatalf("Failed to create batch mode: %v", err)
}
defer batchMode.Close()

// Perform high-speed in-memory searches
results := batchMode.Search("quick brown fox", tokenizer, 10)

// Check memory usage
estimatedBytes, docCount, termCount := batchMode.GetMemoryStats()
fmt.Printf("Memory: %s, Docs: %d, Terms: %d\n", 
    formatBytes(estimatedBytes), docCount, termCount)

// Refresh data when database changes
if needsRefresh {
    err := batchMode.Refresh()
    if err != nil {
        log.Printf("Failed to refresh: %v", err)
    }
}
```

### Memory Estimation

The BatchMode automatically estimates memory requirements:

```go
// Get memory statistics
estimatedBytes, docCount, termCount := batchMode.GetMemoryStats()

// Typical memory usage:
// - 200K documents, avg 100 words: ~100-200MB
// - 200K documents, avg 500 words: ~500MB-1GB
// - 200K documents, avg 1000 words: ~1-2GB
```

### Synchronization

BatchMode maintains consistency with the database:

```go
// Check when data was last synchronized
lastSync := batchMode.GetLastSyncTime()

// Manually refresh when needed
err := batchMode.Refresh()

// Monitor sync status
if time.Since(lastSync) > 1*time.Hour {
    log.Println("Data may be stale, consider refreshing")
}
```

### Performance Comparison

| Operation | PostgreSQL | Batch Mode | Improvement |
|-----------|------------|------------|-------------|
| Single search | 10-50ms | 0.1-1ms | 10-500x |
| 100 searches | 1-5s | 10-100ms | 10-500x |
| Term stats | 5-20ms | 0.01-0.1ms | 50-2000x |
| Document freq | 10-30ms | 0.01-0.1ms | 100-3000x |

### Best Practices for Batch Mode

1. **Memory Management**
   - Monitor memory usage with `GetMemoryStats()`
   - Ensure sufficient RAM for your dataset
   - Consider document content length in memory planning

2. **Refresh Strategy**
   - Refresh during low-traffic periods
   - Use `GetLastSyncTime()` to monitor staleness
   - Implement automatic refresh based on time or change detection

3. **Error Handling**
   - Always check for errors during batch mode creation
   - Implement fallback to regular PostgreSQL mode if needed
   - Handle refresh failures gracefully

4. **Resource Cleanup**
   - Use `defer batchMode.Close()` to release memory
   - Close batch mode when switching to regular mode
   - Monitor memory usage in long-running applications

### Limitations

- **Memory Constraints**: Limited by available RAM
- **Initialization Cost**: One-time cost to load data
- **Data Staleness**: May not reflect recent database changes
- **Single Instance**: Each batch mode instance loads its own copy

## Contributing

When contributing to the PostgreSQL integration:

1. **Test Database**: Ensure tests work with both local and CI PostgreSQL instances
2. **Error Handling**: Provide meaningful error messages for database operations
3. **Performance**: Consider the impact of changes on database performance
4. **Documentation**: Update this README for any new features or changes

## License

This PostgreSQL integration is part of the BM25 Go library and is available under the same MIT License. 