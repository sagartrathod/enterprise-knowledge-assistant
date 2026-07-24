"""
Application-wide constants.

Enterprise AI Knowledge Assistant
"""

# ==========================================================
# Embedding Models
# ==========================================================

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# all-MiniLM-L6-v2 embedding size
EMBEDDING_DIMENSION = 384

# ==========================================================
# LLM
# ==========================================================

GROQ_MODEL = "llama-3.3-70b-versatile"

# ==========================================================
# Cross Encoder
# ==========================================================

RERANKER_MODEL = "BAAI/bge-reranker-base"

# ==========================================================
# File Upload
# ==========================================================

PDF_MAX_FILE_SIZE_MB = 25

ALLOWED_EXTENSIONS = {
    "pdf",
}

# ==========================================================
# pgvector
# ==========================================================

COSINE_DISTANCE_OP = "<=>"

# ==========================================================
# PDF Chunking
# ==========================================================

# Around 350–450 tokens after embedding
CHUNK_MAX_WORDS = 450

# Preserve context between chunks
CHUNK_OVERLAP_WORDS = 100

# Ignore tiny chunks
MIN_CHUNK_WORDS = 20

# ==========================================================
# Retrieval
# ==========================================================

# Initial semantic candidates
SEMANTIC_TOP_K = 50

# Initial BM25 candidates
BM25_TOP_K = 50

# Candidates after hybrid merge
HYBRID_TOP_K = 50

# Reciprocal Rank Fusion constant
RRF_K = 60

# ==========================================================
# Reranker
# ==========================================================

# Chunks sent to CrossEncoder
RERANK_TOP_K = 25

# ==========================================================
# Context Builder
# ==========================================================

# Final chunks sent to LLM
FINAL_TOP_K = 8

# Keep weaker but potentially useful chunks
SIMILARITY_THRESHOLD = 0.20

# Remove duplicated chunks
REMOVE_DUPLICATE_CHUNKS = True

# Remove highly similar chunks
REMOVE_NEAR_DUPLICATES = True

# Text similarity threshold
DUPLICATE_TEXT_THRESHOLD = 0.90

# ==========================================================
# Ranking Strategy
# ==========================================================

# After reranking, rerank score becomes primary ranking
USE_RERANKER = True

# Final ranking priority:
#
# 1. rerank_score
# 2. semantic similarity
# 3. rrf_score
#
SORT_BY_RERANK = True

# If reranker disabled
SORT_BY_SIMILARITY = False

# ==========================================================
# Prompt Behaviour
# ==========================================================

PRIMARY_CHUNK_PRIORITY = True

STOP_AFTER_PRIMARY_IF_COMPLETE = False

SHOW_RETRIEVAL_SCORES = False

SHOW_LINE_NUMBERS = True

SHOW_DOCUMENT_METADATA = True

# ==========================================================
# Query Expansion
# ==========================================================

ENABLE_QUERY_NORMALIZATION = True

ENABLE_QUERY_EXPANSION = False

# ==========================================================
# Answer Generation
# ==========================================================

DEFAULT_NO_ANSWER = (
    "I cannot find the answer based on the provided document chunks."
)

DEFAULT_RAG_TOP_K = HYBRID_TOP_K

# ==========================================================
# LLM Parameters
# ==========================================================

LLM_TEMPERATURE = 0.0

LLM_TOP_P = 1.0

LLM_MAX_TOKENS = 2048

LLM_FREQUENCY_PENALTY = 0.0

LLM_PRESENCE_PENALTY = 0.0

# ==========================================================
# Logging
# ==========================================================

LOG_RETRIEVAL = True
LOG_RERANKING = True
LOG_CONTEXT = True
LOG_PROMPT = False

# Compatibility with existing services
LOG_PRIMARY_CHUNK = True
LOG_FINAL_CONTEXT = True
LOG_HYBRID_SEARCH = True
LOG_SEMANTIC_SEARCH = True
LOG_BM25_SEARCH = True
LOG_CITATIONS = True
LOG_RAG_PIPELINE = True