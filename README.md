# PMI — Project Memory Intelligence

> Search a repository's history, retrieve project context, and explore AI-assisted pull request review.

PMI is a Python prototype that collects GitHub commits, issues, pull requests, and Markdown documentation into a local project memory. It combines deterministic lookups with retrieval-augmented generation (RAG), exposed through a FastAPI backend and Streamlit UI.

**Status:** local-development prototype. The repository contains the implementation, but no tracked automated test suite or published quality benchmark. Read [current limitations](#current-limitations) before deployment.

[Features](FEATURES.md) · [Architecture](#architecture) · [Setup](#setup) · [Testing](#testing) · [Contributing](CONTRIBUTING.md)

## Features

- **Repository collection:** commit metadata and changed filenames; issues excluding PR records; pull requests with merge state, linked issue references, and changed filenames; recursively collected Markdown documents.
- **Exact questions:** entity lookup, type lists, first/last and previous/next chronological records, and the union of changed filenames.
- **Semantic questions:** sentence-transformers embeddings, persistent ChromaDB storage, vector retrieval with lexical reranking and a documentation boost for project-level questions.
- **Chat interface:** sign-up, sign-in, bearer-token authentication, per-user chat storage, and an explicit active reference for follow-ups.
- **PR analysis:** a GitHub Actions workflow collects project memory and posts a generated analysis comment for opened or synchronized pull requests.

Generated answers and reviews require human verification. A model's instruction to report confirmed issues is not a guarantee of correctness.

## Architecture

```text
GitHub API
    |
    v
Collection -> JSON records -> Knowledge documents -> MiniLM embeddings
                                                         |
                                                         v
                                                  Persistent ChromaDB
                                                         |
                  +--------------------------------------+
                  |
Streamlit UI -> FastAPI /chat -> Rule-based query planner
    |                              |                 |
    v                              v                 v
SQLite chats                 Exact lookup      Hybrid retrieval
and users                    and formatting          |
                                                     v
                                              OpenRouter model
                                                     |
                                                     v
                                                Chat answer

GitHub Actions -> rebuild memory -> PR patches + retrieved history
                                      |
                                      v
                               OpenRouter analysis -> PR comment
```

| Component | Implementation | Responsibility |
| --- | --- | --- |
| Collection | [src/collect.py](src/collect.py), `fetch_*.py` | Fetch repository history and Markdown through PyGithub |
| Preparation | [src/pipeline.py](src/pipeline.py), [knowledge builder](src/build_knowledge_base.py) | Run collection, normalization, embedding, and indexing |
| Embeddings | [src/Embeddings/generator.py](src/Embeddings/generator.py) | Locally encode text with `all-MiniLM-L6-v2` |
| Index | [src/VectorDB/indexer.py](src/VectorDB/indexer.py) | Recreate the `pmi_knowledge_chroma` collection and upsert current records |
| Retrieval | [planner](src/Retrieval/planner.py), [queries](src/Retrieval/query.py) | Route structured questions without a model; retrieve/rerank semantic context |
| Reasoning | [src/Reasoning/llm.py](src/Reasoning/llm.py) | Call the OpenRouter endpoint with the configured model |
| API and authentication | [src/API/main.py](src/API/main.py), [Auth](src/API/Auth) | Authenticate users and serve answers |
| UI and persistence | [src/UI/app.py](src/UI/app.py), [chat repository](src/Database/chat_repository.py) | Call the API and write chats directly to the shared SQLite database |
| PR reviewer | [src/DevOps](src/DevOps), [workflow](.github/workflows/pmi-pr.yml) | Retrieve history, analyze bounded patches, and post a PR comment |

The API and UI are intended to run from the same checkout: the UI accesses SQLite directly, rather than using a separate chat-storage API. All users share the configured repository index.

### Data and reference behavior

Preparation writes raw JSON under `data/`, processed documents under `data/processed/`, and ChromaDB under `data/chroma/`. User accounts and chats use `data/pmi.db`.

The pipeline rebuilds the current Chroma collection; it is not a multi-repository archive. Refreshes replace the indexed snapshot and may take time on large repositories.

Canonical IDs use `commit_<7-character-sha>`, `pr_<number>`, `issue_<number>`, and `doc_<filename-with-dots-replaced>`. Filename-based document IDs can collide when different directories contain the same filename.

The client sends `active_reference` explicitly. The current API updates it from a returned record after exact or relative retrieval; previous/next navigation does **not** promise a fixed original anchor. PR reference-prefix handling and clearing persisted references require further validation. The `history` field is accepted but is not used by the chat handler as conversational model context.

## Setup

### Prerequisites

- Python with virtual-environment support. Source syntax requires Python 3.10 or later; the repository does not declare or lock a fully tested Python/dependency combination.
- GitHub access to a repository you are authorized to index.
- Internet access for dependencies and the initial embedding-model download.
- An OpenRouter key for semantic answers and PR analysis.

### 1. Clone and install

```bash
git clone https://github.com/MohyeldinM-Mady/PMI-Devops-Assistant_prototype.git
cd PMI-Devops-Assistant_prototype
python -m venv .venv
```

Activate the environment:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

Then install the declared dependencies:

```bash
python -m pip install -r requirements.txt
```

Several dependencies are unpinned, and the manifest includes ML packages beyond the active OpenRouter reasoning path. Installation compatibility depends on the platform. Report the Python version and exact installation error if setup fails.

### 2. Configure the environment

Copy [.env.example](.env.example) to `.env` in the repository root and replace the placeholders:

```env
GITHUB_TOKEN=your_github_token_here
REPO_OWNER=owner_name
REPO_NAME=repository_name
OPENROUTER_API_KEY=your_openrouter_api_key
LLM_MODEL=openrouter/free
COOKIES_PASSWORD=use-a-long-random-cookie-secret
```

- GitHub configuration is required for collection. Grant only the repository access needed for the intended source.
- `OPENROUTER_API_KEY` is required when invoking semantic reasoning or PR analysis.
- `LLM_MODEL` selects the OpenRouter model; provider availability and pricing can change.
- `COOKIES_PASSWORD` encrypts the UI cookie. It does **not** configure JWT signing.
- The example also contains `HF_TOKEN`; the embedding implementation does not explicitly read it.

**Local use only:** [authentication security](src/API/Auth/security.py) currently hardcodes a placeholder JWT signing key instead of reading a secret from the environment. Merely adding a JWT variable to `.env` does not fix this. Replace that implementation and review deployment security before exposing the app to other users.

### 3. Prepare project memory

Run from the repository root:

```bash
python -m src.pipeline
```

This performs collection, knowledge-base construction, embedding generation, and a ChromaDB rebuild. The UI's **Prepare Repository** control invokes the same pipeline.

### 4. Start API and UI

In one terminal with the virtual environment activated:

```bash
python -m uvicorn src.API.main:app --reload --host 127.0.0.1 --port 8000
```

In another terminal from the same checkout:

```bash
python -m streamlit run src/UI/app.py --server.address 127.0.0.1
```

Open the Streamlit URL printed by the command, create a local test account, and sign in. The UI's API address is hardcoded to `http://127.0.0.1:8000`. The API exposes interactive documentation at `http://127.0.0.1:8000/docs`.

## Using the API

| Route | Purpose |
| --- | --- |
| `GET /` | Basic API-running message |
| `POST /Auth/signup` | Create an account |
| `POST /Auth/signin` | Obtain a bearer token |
| `GET /Auth/me` | Read the authenticated user |
| `POST /Auth/logout` | Increment the user's token version, invalidating earlier tokens |
| `POST /chat` | Ask a question with bearer authentication |

Example authenticated `/chat` body (replace the PR number with one in your indexed repository):

```json
{
  "question": "What files did it change?",
  "history": [],
  "active_reference": {
    "entity": "pull_request",
    "identifier": "15"
  }
}
```

The response includes `question`, `answer`, the retrieval `plan`, and the next `active_reference`.

Try “Show me all commits”, “Show me all changed files”, an explicit commit/PR lookup, and “What is the purpose of the project?”. Structured questions use deterministic operations; semantic questions retrieve context before calling the model.

## GitHub Actions PR analysis

[The workflow](.github/workflows/pmi-pr.yml) runs on PR `opened` and `synchronize` events. It installs dependencies, rebuilds memory, and invokes `python -m src.DevOps.main`.

It uses the workflow-provided `GITHUB_TOKEN`, repository information, PR number, and an `OPENROUTER_API_KEY` repository secret. Its model is set to `openrouter/free`. Fork-origin PRs normally lack repository secrets and write-token permissions, so this workflow should not be presented as supporting every external contribution automatically.

The reviewer currently sends at most **5 files**, **200 patch characters per file**, **1,000 patch characters total**, and **300 historical-context characters** to its analysis prompt. It posts a top-level PR comment, not inline review findings. These small limits make it a demonstration of integration, not exhaustive code review.

Local invocation additionally needs `GITHUB_REPOSITORY=owner/name` and `PR_NUMBER`. Running the DevOps entry point **posts a comment**; it is not a read-only test.

Semantic questions and PR analysis send selected repository content to OpenRouter and the chosen model provider. Index only material whose processing and disclosure you are authorized to permit.

## Testing

There is no tracked automated test suite in this repository. The PR-analysis workflow is not a test workflow, and the commands below are a manual validation procedure—not a claim that an end-to-end run has passed.

1. Use a small repository with known commits, issues, PRs, and Markdown.
2. Run `python -m src.pipeline`; inspect the generated JSON and confirm the expected records were collected.
3. Start the API and verify `GET /` and `/docs`.
4. Sign up and sign in through the UI. Verify an unauthenticated `POST /chat` is rejected.
5. Compare an exact entity lookup and a changed-file list with GitHub.
6. Exercise previous/next navigation and PR follow-ups, checking the returned `active_reference` against the limitations above.
7. Ask a semantic question and compare its answer with the retrieved source material.
8. Refresh the UI, check persisted chat history, then log out and confirm the old token is rejected.

A lightweight syntax check is `python -m compileall -q src`; it does not validate dependencies, credentials, retrieval quality, or runtime behavior.

## Outcomes and scope

The implementation connects GitHub collection, structured retrieval, vector search, an authenticated web interface, local persistence, and automated PR commenting in one prototype. It demonstrates a design in which exact metadata questions avoid an LLM call while semantic questions use retrieved evidence.

No measured productivity improvement, answer-accuracy score, review-detection rate, production adoption, or test-coverage percentage is established by the repository. Those outcomes need a reproducible evaluation before they can be claimed.

## Current limitations

- Placeholder JWT signing key; shared repository index; local API/UI database coupling.
- No tracked automated tests or reproducible quality benchmark; dependencies are only partially pinned.
- Reference handling and filename-based IDs need regression coverage.
- Collection fetches history and Markdown, not a complete semantic index of source-code bodies or discussion threads.
- Full refreshes and lexical scans can become costly as repository history grows.
- Generated answers may be incorrect despite grounding instructions; PR patch truncation can omit decisive evidence.

## Contributing and attribution

See [CONTRIBUTING.md](CONTRIBUTING.md) for scope, validation, and review expectations. Preserve contributor attribution in Git history.

Portfolio contact: **[Mohyeldin M. Yakout](https://www.linkedin.com/in/mohyeldin-mady-yakout)**.

No license file is currently present in this repository. Public visibility alone should not be treated as an explicit open-source license.
