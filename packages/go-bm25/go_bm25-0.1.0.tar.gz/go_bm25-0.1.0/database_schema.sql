-- PostgreSQL Database Schema for BM25 Index
-- This schema stores documents, terms, and their relationships for BM25 scoring

-- Enable UUID extension if needed
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Documents table - stores document metadata and content
CREATE TABLE IF NOT EXISTS documents (
    doc_id SERIAL PRIMARY KEY,
    doc_identifier VARCHAR(255) UNIQUE NOT NULL,
    doc_content TEXT,
    total_terms INTEGER NOT NULL DEFAULT 0,
    unique_terms INTEGER NOT NULL DEFAULT 0,
    doc_length REAL NOT NULL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Terms table - stores unique terms and their global statistics
CREATE TABLE IF NOT EXISTS terms (
    term_id SERIAL PRIMARY KEY,
    term_text VARCHAR(100) UNIQUE NOT NULL,
    doc_frequency INTEGER NOT NULL DEFAULT 0,  -- Number of documents containing this term
    total_frequency INTEGER NOT NULL DEFAULT 0,  -- Total occurrences across all documents
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Term-document relationships - stores term frequencies within documents
CREATE TABLE IF NOT EXISTS term_document_freqs (
    term_id INTEGER REFERENCES terms(term_id) ON DELETE CASCADE,
    doc_id INTEGER REFERENCES documents(doc_id) ON DELETE CASCADE,
    term_frequency INTEGER NOT NULL DEFAULT 0,  -- Frequency of term in this document
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (term_id, doc_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_documents_identifier ON documents(doc_identifier);
CREATE INDEX IF NOT EXISTS idx_terms_text ON terms(term_text);
CREATE INDEX IF NOT EXISTS idx_term_doc_freqs_term ON term_document_freqs(term_id);
CREATE INDEX IF NOT EXISTS idx_term_doc_freqs_doc ON term_document_freqs(doc_id);
CREATE INDEX IF NOT EXISTS idx_term_doc_freqs_composite ON term_document_freqs(term_id, doc_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to automatically update updated_at
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_terms_updated_at BEFORE UPDATE ON terms
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_term_doc_freqs_updated_at BEFORE UPDATE ON term_document_freqs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate BM25 score
CREATE OR REPLACE FUNCTION calculate_bm25_score(
    p_term TEXT, 
    p_doc_id INTEGER,
    p_k1 REAL DEFAULT 1.2,
    p_b REAL DEFAULT 0.75
) RETURNS REAL AS $$
DECLARE
    v_idf REAL;
    v_term_freq INTEGER;
    v_doc_length REAL;
    v_avg_doc_length REAL;
    v_doc_frequency INTEGER;
    v_total_docs INTEGER;
BEGIN
    -- Get document frequency for the term
    SELECT doc_frequency INTO v_doc_frequency
    FROM terms WHERE term_text = p_term;
    
    IF v_doc_frequency IS NULL THEN
        RETURN 0.0;  -- Term not found
    END IF;
    
    -- Get total number of documents
    SELECT COUNT(*) INTO v_total_docs FROM documents;
    
    -- Calculate IDF (Inverse Document Frequency)
    v_idf = LN((v_total_docs::REAL - v_doc_frequency + 0.5) / (v_doc_frequency + 0.5));
    
    -- Get term frequency in the specific document
    SELECT tdf.term_frequency INTO v_term_freq
    FROM term_document_freqs tdf
    JOIN terms t ON t.term_id = tdf.term_id
    WHERE t.term_text = p_term AND tdf.doc_id = p_doc_id;
    
    IF v_term_freq IS NULL THEN
        RETURN 0.0;  -- Term not found in document
    END IF;
    
    -- Get document length and average document length
    SELECT doc_length INTO v_doc_length FROM documents WHERE doc_id = p_doc_id;
    SELECT AVG(doc_length) INTO v_avg_doc_length FROM documents;
    
    -- Handle case where average might be NULL
    IF v_avg_doc_length IS NULL OR v_avg_doc_length = 0.0 THEN
        v_avg_doc_length = 1.0;  -- Avoid division by zero
    END IF;
    
    -- Calculate BM25 score
    RETURN v_idf * (v_term_freq * (p_k1 + 1.0)) / 
           (v_term_freq + p_k1 * (1.0 - p_b + p_b * (v_doc_length / v_avg_doc_length)));
END;
$$ LANGUAGE plpgsql;

-- Function to search documents by multiple terms and return BM25 scores
CREATE OR REPLACE FUNCTION search_documents_bm25(
    p_terms TEXT[],
    p_k1 REAL DEFAULT 1.2,
    p_b REAL DEFAULT 0.75,
    p_limit INTEGER DEFAULT 10
) RETURNS TABLE(
    doc_id INTEGER,
    doc_identifier VARCHAR(255),
    total_score REAL,
    doc_content TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.doc_id,
        d.doc_identifier,
        SUM(calculate_bm25_score(term, d.doc_id, p_k1, p_b)) AS total_score,
        d.doc_content
    FROM documents d
    CROSS JOIN UNNEST(p_terms) AS term
    WHERE EXISTS (
        SELECT 1 FROM term_document_freqs tdf
        JOIN terms t ON t.term_id = tdf.term_id
        WHERE t.term_text = term AND tdf.doc_id = d.doc_id
    )
    GROUP BY d.doc_id, d.doc_identifier, d.doc_content
    ORDER BY total_score DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Function to get term statistics
CREATE OR REPLACE FUNCTION get_term_statistics(p_term TEXT)
RETURNS TABLE(
    term_text TEXT,
    doc_frequency INTEGER,
    total_frequency INTEGER,
    documents_info TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.term_text,
        t.doc_frequency,
        t.total_frequency,
        STRING_AGG(
            CONCAT('Doc ', d.doc_identifier, ' (freq: ', tdf.term_frequency, ')'),
            ', ' ORDER BY d.doc_identifier
        ) AS documents_info
    FROM terms t
    LEFT JOIN term_document_freqs tdf ON t.term_id = tdf.term_id
    LEFT JOIN documents d ON tdf.doc_id = d.doc_id
    WHERE t.term_text = p_term
    GROUP BY t.term_id, t.term_text, t.doc_frequency, t.total_frequency;
END;
$$ LANGUAGE plpgsql;

-- Function to get index statistics
CREATE OR REPLACE FUNCTION get_index_statistics()
RETURNS TABLE(
    total_documents INTEGER,
    total_unique_terms INTEGER,
    average_document_length REAL,
    total_term_occurrences BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(DISTINCT d.doc_id)::INTEGER AS total_documents,
        COUNT(DISTINCT t.term_id)::INTEGER AS total_unique_terms,
        AVG(d.doc_length) AS average_document_length,
        SUM(t.total_frequency) AS total_term_occurrences
    FROM documents d
    CROSS JOIN terms t;
END;
$$ LANGUAGE plpgsql;

-- Sample data insertion (optional)
-- INSERT INTO documents (doc_identifier, doc_content, total_terms, unique_terms, doc_length) VALUES
--     ('doc1', 'The quick brown fox jumps over the lazy dog', 9, 8, 9.0),
--     ('doc2', 'A quick brown dog runs fast', 6, 6, 6.0),
--     ('doc3', 'The lazy fox sleeps in the sun', 7, 7, 7.0);

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_user; 