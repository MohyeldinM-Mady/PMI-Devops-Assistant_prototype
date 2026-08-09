# PMI Data Collection & Knowledge Extraction

Phase 1 - 3 of the PMI (Project Memory Intelligence) pipeline.

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
## Status

- ✅ Phase 1 — Data Collection: complete
- ✅ Phase 2 — Knowledge Extraction: complete
- ✅ Phase 3 — Embedding Generation: complete
- ⬜ Phase 4 — Knowledge Database: next up for the team
- ⬜ Phase 5–9: downstream phases (RAG retrieval, AI reasoning, UI, intelligent features, DevOps integration)
