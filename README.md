# PMI — Project Memory Intelligence

PMI is a GitHub-centric project-memory and DevOps assistant. It collects a repository's commits, issues, pull requests, and Markdown documentation; turns them into structured knowledge; generates embeddings; indexes the knowledge in ChromaDB; and exposes both a retrieval/reasoning API and an automated Pull Request reviewer.

## Architecture

```text
GitHub Repository
       │
       ▼
Phase 1 — Collection
       │
       ▼
Phase 2 — Knowledge Extraction
       │
       ▼
Phase 3 — Embeddings
       │
       ▼
Phase 4 — ChromaDB
       │
       ▼
Phase 5 — Retrieval
       │
       ├───────────────┐
       ▼               ▼
Phase 7 — API/UI   Phase 9 — DevOps Review
       │               │
       ▼               ▼
     User           GitHub PR
       │               │
       └───────┬───────┘
               ▼
        Phase 6 — Reasoning
```

Phase 8 is not implemented in the current repository, so it is intentionally not described as an implemented phase.

## Key design decisions

### 1. Deterministic project facts stay deterministic

PMI does not send simple structured questions through the reasoning model when the answer can be obtained exactly from the knowledge base.

These operations are deterministic:

- `get` — one commit, PR, issue, or documentation file.
- `list` — all records of one type.
- `previous` — immediately older record by the entity's chronological field.
- `next` — immediately newer record by the entity's chronological field.
- `list_files` — unique union of changed files across commit and PR records.

The LLM is reserved for semantic/project questions where similarity retrieval and reasoning are actually useful.

### 2. Active references are explicit

The chatbot keeps an `active_reference` per conversation and sends it to the API. A follow-up such as:

```text
Tell me about PR #15
What files did it change?
What was the previous PR?
What was the next PR?
```

keeps the reference anchored to PR #15. `previous` and `next` never replace the active reference with the record they return.

Conversation history is retained by the UI for display, but it is no longer used as the primary reference-resolution mechanism.

### 3. Canonical entity IDs

| Entity | ID format |
|---|---|
| Commit | `commit_<7-char-sha>` |
| Pull request | `pr_<number>` |
| Issue | `issue_<number>` |
| Documentation | `doc_<filename-with-dots-replaced>` |

All retrieval code uses the same canonical-ID function.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and configure:

```env
GITHUB_TOKEN=your_github_token_here
REPO_OWNER=owner_name
REPO_NAME=repo_name
HF_TOKEN=your_huggingface_token
LLM_MODEL=Qwen/Qwen2.5-3B-Instruct
```

Do not commit `.env` or tokens.

## Full repository preparation

The complete local preparation pipeline is:

```bash
python -m src.pipeline
```

It runs:

1. Collection
2. Knowledge-base construction
3. Embedding generation
4. ChromaDB rebuild

The vector database is rebuilt rather than only upserted so deleted or stale repository records cannot survive between refreshes.

### Phase 1 — Data Collection

```bash
python -m src.collect
```

Produces:

- `data/commits.json`
- `data/issues.json`
- `data/pull_requests.json`
- `data/docs.json`

### Phase 2 — Knowledge Extraction

```bash
python -m src.build_knowledge_base
```

Produces:

- `data/processed/knowledge_base.json`

Each knowledge document has a stable ID, entity type, human-readable text, and structured metadata.

### Phase 3 — Embeddings

```bash
python -m src.Embeddings.main
```

Uses `all-MiniLM-L6-v2` and produces:

- `data/processed/embedded_documents.json`

### Phase 4 — Vector Database

```bash
python -m src.VectorDB.main
```

The indexer recreates the PMI Chroma collection and indexes the current embedded dataset. This avoids stale records after a repository refresh.

### Phase 5 — Retrieval

The retrieval layer supports:

- semantic similarity search
- exact entity lookup
- type listing
- chronological previous/next lookup
- unique changed-file aggregation

Run the retrieval demo with:

```bash
python -m src.Retrieval.main
```

### Phase 6 — AI Reasoning

The reasoning layer uses the Hugging Face Inference API only when semantic reasoning is needed. Project content is explicitly treated as untrusted data so repository text cannot act as instructions to the model.

Run the standalone reasoning demo with:

```bash
python -m src.Reasoning.main
```

### Phase 7 — Chatbot API and UI

Start the API:

```bash
uvicorn src.API.main:app --reload
```

Start Streamlit in another terminal:

```bash
streamlit run src/UI/app.py
```

The API endpoint is:

```text
POST /chat
```

The request can include:

```json
{
  "question": "what files did it change?",
  "history": [],
  "active_reference": {
    "entity": "pull_request",
    "identifier": "15"
  }
}
```

The response returns the answer, the validated retrieval plan, and the next active reference.

### Phase 9 — GitHub Actions DevOps Review

The workflow is located at:

```text
.github/workflows/pmi-pr.yml
```

It runs when a PR is opened or synchronized and performs:

1. Collect repository history.
2. Build the knowledge base.
3. Generate embeddings.
4. Rebuild ChromaDB.
5. Retrieve historical context for the current PR changes.
6. Generate a security-aware AI review.
7. Post the review as a PR comment.

## Project structure

```text
src/
├── config.py
├── github_client.py
├── collect.py
├── build_knowledge_base.py
├── pipeline.py
├── fetch_commits.py
├── fetch_issues.py
├── fetch_pull_requests.py
├── fetch_docs.py
├── process_commits.py
├── process_issues.py
├── process_pull_requests.py
├── process_docs.py
│
├── Embeddings/
│   ├── loader.py
│   ├── generator.py
│   ├── builder.py
│   └── main.py
│
├── VectorDB/
│   ├── database.py
│   ├── loader.py
│   ├── indexer.py
│   ├── query.py
│   └── main.py
│
├── Retrieval/
│   ├── schema.py
│   ├── planner.py
│   ├── embedder.py
│   ├── query.py
│   ├── context.py
│   └── main.py
│
├── Reasoning/
│   ├── llm.py
│   ├── prompt.py
│   └── main.py
│
├── API/
│   └── main.py
│
├── UI/
│   └── app.py
│
└── DevOps/
    ├── github.py
    ├── retrieval.py
    ├── analyzer.py
    └── main.py

tests/
└── test_retrieval_contract.py
```

## Retrieval examples

### Exact entity

```text
Tell me about commit 03b92a8
```

### Follow-up

```text
What files did it change?
```

### Relative navigation

```text
What was the previous commit?
What was the next commit?
```

### Deterministic lists

```text
Show me all commits
Show me all pull requests
Show me all documentation files
Show me all changed files
```

### Semantic question

```text
What is the purpose of the project?
```

The last type uses semantic retrieval and the reasoning model; the structured examples do not need a second reasoning pass.

## Testing

Run the retrieval-contract tests with:

```bash
python -m pytest -q
```

The tests cover canonical IDs, explicit references, active-reference follow-ups, relative navigation, and the dedicated `list_files` operation.
