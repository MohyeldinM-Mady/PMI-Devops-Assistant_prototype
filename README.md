# PMI Data Collection & Knowledge Extraction

Phase 1 - 5 of the PMI (Project Memory Intelligence) pipeline.

## What this does

This project pulls a GitHub repository's history (commits, issues, pull
requests, and documentation) and turns it into a structured knowledge base
of human-readable documents — ready to be embedded and searched in later
phases (embeddings, vector DB, RAG retrieval).

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill in your GitHub credentials:
   ```
   GITHUB_TOKEN=your_personal_access_token
   REPO_OWNER=repo_owner_username
   REPO_NAME=repo_name
   ```
   Your token needs `repo` scope, and you need collaborator access if the
   target repo is private.

## Running the full pipeline

**Step 1 — Data Collection (Phase 1):**
Pulls raw data from the GitHub API and saves it as JSON.
```
python -m src.collect
```
Output: `data/commits.json`, `data/issues.json`, `data/pull_requests.json`, `data/docs.json`

**Step 2 — Knowledge Extraction (Phase 2):**
Reads the raw JSON files and converts each item into a readable text
document with metadata, ready for embedding.
```
python -m src.build_knowledge_base
```
Output: `data/processed/knowledge_base.json`


**Step 3 — Embedding Generation (Phase 3):**
Reads the processed knowledge base and converts each knowledge document
into a vector embedding using Sentence Transformers.

```
python -m src.Embeddings.main
```

Output: `data/processed/embedded_documents.json`

Each embedded document preserves the original ID, type, text, metadata,
and its generated embedding vector.

**Step 4 — Vector Database (Phase 4):**

Loads the generated embeddings and indexes them into a persistent ChromaDB
collection. The vector database stores document text, embeddings, and
metadata, and supports similarity search and metadata filtering.

```bash
uv run python -m src.VectorDB.main
```
**Step 5 — Retrieval (RAG):**

Receives a user question, converts it into a vector embedding using the
same Sentence Transformer model used during Phase 3, and performs semantic
similarity search against the ChromaDB vector store.

The retrieval layer returns the most relevant project documents and formats
them into clean context ready for the LLM.

Run Phase 5 with:

```bash
uv run python -m src.Retrieval.main
```

## Project structure

```
├── data/
│   ├── commits.json, issues.json, pull_requests.json, docs.json   (Phase 1 output)
│   └── processed/
│       ├── knowledge_base.json                                     (Phase 2 output — final deliverable)
|       └── embedded_documents.json           (Phase 3 output)
└── src/
    ├── config.py                  # loads and validates environment variables
    ├── github_client.py           # GitHub authentication
    ├── collect.py                 # Phase 1 orchestrator
    ├── fetch_commits.py
    ├── fetch_issues.py
    ├── fetch_pull_requests.py
    ├── fetch_docs.py
    ├── build_knowledge_base.py    # Phase 2 orchestrator
    ├── process_commits.py
    ├── process_issues.py
    ├── process_pull_requests.py
    ├── process_docs.py
    ├── Embeddings/               #phase 3
    │   ├── __init__.py
    │   ├── loader.py              # loads knowledge base documents
    │   ├── generator.py           # generates vector embeddings
    │   ├── builder.py             # builds and saves embedded documents
    │   └── main.py                # Phase 3 orchestrator
    ├── VectorDB/                              # Phase 4
    │   ├── __init__.py
    │   ├── loader.py                          # loads embedded documents
    │   ├── database.py                        # ChromaDB client and collection
    │   ├── indexer.py                         # indexes documents into ChromaDB
    │   ├── query.py                           # similarity search and filtering
    │   └── main.py                            # Phase 4 orchestrator
    └── Retrieval/                  # Phase 5
        ├── __init__.py
        ├── embedder.py             # embeds user queries
        ├── query.py                # retrieves relevant documents
        ├── context.py              # builds clean retrieved context
        └── main.py                 # Phase 5 orchestrator
```

## Knowledge base document format

Each entry in `knowledge_base.json` looks like this:
```json
{
  "id": "commit_42b1f06",
  "type": "commit",
  "text": "On 2026-08-07..., a human-readable summary of the event.",
  "metadata": { "...": "raw structured fields for filtering/display" }
}
```
## Embedding Output

Each embedded document contains the original knowledge document
alongside its generated vector embedding:

```json
{
  "id": "commit_42b1f06",
  "type": "commit",
  "text": "Human-readable project event summary.",
  "embedding": [0.012, -0.034, 0.056],
  "metadata": {
    "...": "original metadata"
  }
}
```
## Vector Database

Phase 4 uses ChromaDB as the project's vector database.

The embedding pipeline stores each knowledge document with:

- Document ID
- Document text
- Vector embedding
- Metadata
- Document type

The database supports:

- Persistent local storage
- Similarity search
- Top-K retrieval
- Metadata filtering

Example:

```python
similarity_search(
    "Who worked on RAG documentation?",
    n_results=3,
    where={"type": "commit"}
)
```
## Retrieval

Phase 5 implements the retrieval layer of the RAG pipeline.

It converts user questions into embeddings using the same Sentence Transformer
model used during Phase 3, performs semantic similarity search against
ChromaDB, and builds a clean context from the most relevant project documents.

The retrieved context includes:

- Document type
- Document ID
- Author
- Date
- Document content

Example:

```python
retrieve_context(
    "What changes were made to the RAG system?",
    n_results=3
)
```
## Status

- ✅ Phase 1 — Data Collection: complete
- ✅ Phase 2 — Knowledge Extraction: complete
- ✅ Phase 3 — Embedding Generation: complete
- ✅ Phase 4 — Knowledge Database: complete
- ✅ Phase 5 — RAG Retrieval: complete
- ⬜ Phase 6 — AI Reasoning
- ⬜ Phase 7 — User Interface
- ⬜ Phase 8 — Intelligent Features
- ⬜ Phase 9 — DevOps Integration
