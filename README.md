# PMI Data Collection & Knowledge Extraction

Phases 1–7 and Phase 9 of the PMI (Project Memory Intelligence) pipeline.

## What this does

This project pulls a GitHub repository's history (commits, issues, pull
requests, and documentation) and transforms it into structured project
knowledge that can be embedded, indexed, retrieved, and used to generate
context-aware answers.

In Phase 9, PMI is integrated into GitHub Actions to automatically analyze
new and updated Pull Requests and generate AI-powered recommendations based
on the project's historical knowledge.

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
**Step 6 — AI Reasoning:**

Uses a Large Language Model through the Hugging Face Inference API to
generate context-aware answers from the project knowledge retrieved in
Phase 5.

The LLM is instructed to use only the retrieved project context and avoid
inventing project information.

Run Phase 6 with:

```bash
uv run python -m src.Reasoning.main
```
**Step 7 — DevOps Integration:**

Integrates PMI into the GitHub Actions CI/CD pipeline to automatically
analyze new and updated Pull Requests.

When a Pull Request is opened or updated, GitHub Actions runs the PMI
pipeline, retrieves the changed files, searches the project memory for
relevant historical context, and uses the LLM to generate an
AI-powered Pull Request review.

The generated analysis is automatically posted as a comment on the
Pull Request.

The Phase 9 workflow performs the following steps:

1. Collect project history.
2. Build the knowledge base.
3. Generate embeddings.
4. Build the ChromaDB vector database.
5. Retrieve Pull Request changes.
6. Retrieve relevant historical context.
7. Generate an AI-powered Pull Request analysis.
8. Post the analysis as a GitHub Pull Request comment.

The GitHub Actions workflow is located at:

```text
.github/workflows/pmi-pr.yml
```
The workflow is triggered when a Pull Request is opened or updated:
```yaml
on:
  pull_request:
    types: [opened, synchronize]
```
Run Phase 9 automatically through GitHub Actions by opening or updating
a Pull Request.


**Step 7 — Chatbot UI & API (Phase 7):**

Provides a web-based chatbot interface for interacting with the project's
knowledge base.

The chatbot uses a FastAPI backend connected to the existing RAG pipeline.
User questions are retrieved against the ChromaDB vector database, relevant
historical context is built, and the LLM generates a context-aware response.

The chatbot interface is built using Streamlit and supports multiple chat
sessions with conversation history during the active session.

The Phase 7 architecture is:

```text
User
 │
 ▼
Streamlit Chatbot
 │
 ▼
FastAPI /chat
 │
 ▼
RAG Retrieval
 │
 ▼
ChromaDB
 │
 ▼
Historical Context
 │
 ▼
LLM
 │
 ▼
AI Response
```
The API is located at:
```bash
src/API/main.py
```
The chatbot UI is located at:
```bash
src/UI/app.py
```
Run the API with:
```bash
uv run uvicorn src.API.main:app --reload

Run the chatbot UI with:

uv run streamlit run src/UI/app.py
```
The chatbot can answer questions about the project's historical knowledge
and maintain multiple conversations during the active session.


## Project structure

```
├── data/
│   ├── commits.json, issues.json, pull_requests.json, docs.json   (Phase 1 output)
│   └── processed/
│       ├── knowledge_base.json                                     (Phase 2 output — final deliverable)
|       └── embedded_documents.json           (Phase 3 output)
├── .github/
│   └── workflows/
│       └── pmi-pr.yml              # Phase 9 GitHub Actions workflow
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

    ├── Embeddings/                # Phase 3
    │   ├── __init__.py
    │   ├── loader.py              # loads knowledge base documents
    │   ├── generator.py           # generates vector embeddings
    │   ├── builder.py             # builds and saves embedded documents
    │   └── main.py                # Phase 3 orchestrator

    ├── VectorDB/                  # Phase 4
    │   ├── __init__.py
    │   ├── loader.py              # loads embedded documents
    │   ├── database.py            # ChromaDB client and collection
    │   ├── indexer.py             # indexes documents into ChromaDB
    │   ├── query.py               # similarity search and filtering
    │   └── main.py                # Phase 4 orchestrator

    ├── Retrieval/                 # Phase 5
    │   ├── __init__.py
    │   ├── embedder.py            # embeds user queries
    │   ├── query.py               # retrieves relevant documents
    │   ├── context.py             # builds clean retrieved context
    │   └── main.py                # Phase 5 orchestrator

    ├── Reasoning/                 # Phase 6
    │   ├── __init__.py
    │   ├── llm.py                 # Hugging Face LLM API client
    │   ├── prompt.py              # RAG prompt construction
    │   └── main.py                # Phase 6 orchestrator

    ├── API/                       # Phase 7
    │   ├── __init__.py
    │   └── main.py                # FastAPI backend and /chat endpoint

    ├── UI/                        # Phase 7
    │   ├── __init__.py
    │   └── app.py                 # Streamlit chatbot interface

    └── DevOps/                    # Phase 9
        ├── __init__.py
        ├── github.py              # GitHub API integration and PR comments
        ├── retrieval.py           # retrieves historical context for PR changes
        ├── analyzer.py            # generates AI-powered PR analysis
        └── main.py                # Phase 9 orchestrator
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
## AI Reasoning

Phase 6 adds the LLM reasoning layer on top of the retrieval pipeline.

The system sends the user's question together with the relevant project
context retrieved in Phase 5 to an LLM through the Hugging Face Inference API.

The prompt instructs the model to:

- Answer using only the retrieved project context.
- Avoid inventing project information.
- State when the available context is insufficient.
- Provide references to relevant project documents when possible.

The LLM provider and model are configurable through environment variables,
allowing the underlying model to be changed without modifying the RAG
pipeline.

## Architecture

PMI follows a multi-stage pipeline that transforms GitHub project history
into searchable project memory and uses it for both interactive questions
and Pull Request analysis.

```text
GitHub Repository
       │
       ├── Commits
       ├── Issues
       ├── Pull Requests
       └── Documentation
              │
              ▼
      Phase 1 — Data Collection
              │
              ▼
    Phase 2 — Knowledge Extraction
              │
              ▼
    Phase 3 — Embedding Generation
              │
              ▼
       Phase 4 — ChromaDB
              │
              ▼
        Project Memory
              │
       ┌──────┴───────┐
       │              │
       ▼              ▼
 Phase 5 —        Pull Request
 Retrieval        Changes
       │              │
       ▼              ▼
 Historical      Phase 9 —
 Context         DevOps Integration
       │              │
       ▼              ▼
 Phase 6 —       AI PR Analysis
 AI Reasoning        │
       │              ▼
       ▼         GitHub PR Comment
   AI Response
       │
       ▼
 Phase 7 — Chatbot UI & API
       │
       ▼
   User Interaction
Runtime Flow — Chatbot
```
When a user asks a question, the chatbot uses the existing RAG pipeline
to retrieve relevant project history and generate a context-aware answer.
```text
User
  │
  ▼
Streamlit Chatbot
  │
  ▼
FastAPI /chat
  │
  ▼
Phase 5 — Retrieval
  │
  ▼
ChromaDB
  │
  ▼
Historical Context
  │
  ▼
Phase 6 — AI Reasoning
  │
  ▼
AI Response
  │
  ▼
Streamlit UI
Runtime Flow — Pull Request Analysis
```
When a Pull Request is opened or updated, GitHub Actions automatically
triggers PMI.
```text
Pull Request
     │
     ▼
GitHub Actions
     │
     ├── Collect project history
     ├── Build knowledge base
     ├── Generate embeddings
     ├── Build ChromaDB
     │
     ▼
Retrieve PR changes
     │
     ▼
Search project memory
     │
     ▼
Historical context
     │
     ▼
LLM reasoning
     │
     ▼
AI-generated review
     │
     ▼
Post comment on Pull Request
```
This allows PMI to combine the current Pull Request with the project's
historical knowledge before generating recommendations.


## Status

- ✅ Phase 1 — Data Collection: complete
- ✅ Phase 2 — Knowledge Extraction: complete
- ✅ Phase 3 — Embedding Generation: complete
- ✅ Phase 4 — Knowledge Database: complete
- ✅ Phase 5 — RAG Retrieval: complete
- ✅ Phase 6 — AI Reasoning: complete
- ✅ Phase 7 — User Interface: complete
- ⬜ Phase 8 — Intelligent Features
- ✅ Phase 9 — DevOps Integration: complete
