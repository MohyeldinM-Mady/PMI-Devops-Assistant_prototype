# PMI Features and System Integration

## 1. Project Overview

PMI, or Project Memory Intelligence, is a GitHub-aware project-memory and DevOps assistant. It collects repository history and documentation, converts that information into searchable knowledge, and provides two main experiences:

- An authenticated project chatbot for questions about repository history and documentation.
- An automated GitHub Pull Request reviewer powered by repository context and retrieval-augmented generation (RAG).

PMI is designed to keep factual repository lookups deterministic while using an LLM for semantic questions and evidence-based PR analysis.

## 2. Main Features

### Project memory

PMI collects the following information from a configured GitHub repository:

- Commits, including SHA, author, date, message, and changed files.
- Issues, including number, title, author, date, state, labels, and content.
- Pull requests, including number, title, author, date, stat, merge status, linked issues, and changed files.
- Markdown documentation files, including filename, path, and full content.

The collected data is stored locally under `data/` and can be rebuilt whenever the repository changes.

### Grounded project chatbot

The chatbot answers questions using the configured repository memory. It supports:

- Semantic questions such as: `What is the purpose of this project?`
- Exact commit, issue, PR, and documentation lookup.
- Lists of commits, pull requests, issues, documentation files, and changed files.
- Previous and next navigation for chronological repository records.
- Follow-up questions that retain the active commit, issue, PR, or document reference.
- Structured answers containing repository metadata and document content.
- A reasoning fallback for questions that cannot be answered by deterministic operations.

### Deterministic retrieval operations

PMI uses structured retrieval whenever the requested answer is available directly from the knowledge base. Supported operations include:

- `get`: retrieve one entity.
- `list`: retrieve all entities of a type.
- `first`: retrieve the first chronological record.
- `last`: retrieve the last chronological record.
- `previous`: retrieve the record before the active or requested record.
- `next`: retrieve the record after the active or requested record.
- `list_files`: return the unique union of changed files.
- `search`: perform semantic retrieval and use the reasoning model to answer.

This separation reduces unnecessary LLM calls and makes repository facts more predictable.

## 3. RAG Pipeline

PMI uses a retrieval-augmented generation pipeline to ground semantic answers in repository data.

### Step 1: Collection

The collection layer uses the GitHub API to fetch commits, issues, pull requests, and Markdown documentation. The repository is selected through:

```env
GITHUB_TOKEN=...
REPO_OWNER=...
REPO_NAME=...
```

### Step 2: Knowledge extraction

The collected records are normalized into knowledge documents. Each document contains:

- A stable canonical ID.
- An entity type.
- Human-readable text.
- Structured metadata.

Canonical ID examples are:

```text
commit_<7-char-sha>
pr_<number>
issue_<number>
doc_<filename-with-dots-replaced>
```

The knowledge base is saved to:

```text
data/processed/knowledge_base.json
```

### Step 3: Embeddings

PMI converts knowledge-document text into vector embeddings using the `all-MiniLM-L6-v2` sentence-transformers model. The generated embeddings are saved to:

```text
data/processed/embedded_documents.json
```

### Step 4: ChromaDB indexing

The vector database stores the embedded documents in ChromaDB. The index is rebuilt from the current processed data so stale records from an older repository state do not remain available.

### Step 5: Retrieval

For semantic questions, PMI embeds the query, searches ChromaDB, and builds a context from the most relevant repository records.

For structured questions, PMI performs exact metadata and chronological lookups without using the LLM.

### Step 6: Reasoning

When semantic reasoning is required, the retrieved context is passed to an OpenRouter-compatible OpenAI API. The model is instructed to:

- Use only the supplied project context.
- Treat repository content as untrusted data rather than instructions.
- Avoid inventing commits, files, authors, dates, or other facts.
- State clearly when the context does not contain an answer.
- Avoid exposing internal reasoning.

The model is configured through:

```env
OPENROUTER_API_KEY=...
LLM_MODEL=openrouter/free
```

## 4. Authentication and User Sessions

The chatbot is protected by the FastAPI authentication system.

### Account features

Users can:

- Create an account with a username, email, and password.
- Sign in and receive a bearer access token.
- Retrieve their current user profile.
- Log out and invalidate the current token.

Authentication routes are available under `/Auth`:

```text
POST /Auth/signup
POST /Auth/signin
GET  /Auth/me
POST /Auth/logout
```

### Password and token security

- Passwords are stored as hashes, not plaintext values.
- Password verification is performed by the backend.
- JWT access tokens identify the authenticated user.
- Token-version changes invalidate previously issued tokens during logout.
- The Streamlit UI stores the access token in an encrypted browser cookie.
- `COOKIES_PASSWORD` is required to encrypt the persistent UI cookie.

```env
COOKIES_PASSWORD=use-a-long-random-secret
```

### Protected chat API

The `/chat` endpoint requires the authenticated user. Each request may include:

- The current question.
- Optional conversation history for display/context.
- An optional active reference identifying the current commit, issue, PR, or document.

The API validates references against the indexed project memory before returning entity-specific answers.

## 5. FastAPI and Streamlit Integration

The application is split into two cooperating services:

### FastAPI backend

The backend provides:

- Authentication and user management.
- Protected chat requests.
- Query planning.
- Deterministic retrieval operations.
- Semantic retrieval and LLM reasoning.
- Active-reference management.
- Persistent database initialization.
- Interactive API documentation through `/docs`.

Start it with:

```powershell
python -m uvicorn src.API.main:app --reload --port 8000
```

### Streamlit frontend

The UI provides:

- Sign-up and sign-in forms.
- Persistent encrypted authentication cookies.
- Chat sessions stored per authenticated user.
- New-chat and chat-selection controls.
- Project-memory chatbot interface.
- A repository preparation screen.
- User logout.

Start it with:

```powershell
python -m streamlit run src/UI/app.py
```

The UI sends authenticated requests to:

```text
http://127.0.0.1:8000
```

The repository preparation screen calls the same pipeline used from the command line:

```text
Collection -> Knowledge base -> Embeddings -> ChromaDB
```

## 6. DevOps and GitHub Actions Integration

PMI includes an automated PR review workflow at:

```text
.github/workflows/pmi-pr.yml
```

### Workflow triggers

The workflow runs when a pull request is:

- Opened.
- Synchronized with new commits.

### GitHub Actions permissions

The workflow requests:

- `contents: read` to inspect repository content.
- `issues: write` to create the PR comment through GitHub's issues API.
- `pull-requests: write` to support PR review automation.

### PR review workflow stages

1. Check out the repository.
2. Create a Python environment with `uv`.
3. Install CPU-compatible PyTorch and project dependencies.
4. Collect the current repository's commits, issues, pull requests, and documentation.
5. Build the structured knowledge base.
6. Generate embeddings.
7. Rebuild the ChromaDB index.
8. Read the changed files and patches from the current PR.
9. Retrieve historical repository context related to those changes.
10. Send the PR changes and historical context to the reasoning model.
11. Generate a concise review containing only confirmed bugs, regressions, security issues, or broken behavior.
12. Post the analysis as a comment on the pull request.

### Required workflow configuration

The workflow uses the automatic GitHub token for repository access and PR comments:

```text
GITHUB_TOKEN=${{ secrets.GITHUB_TOKEN }}
```

It uses an OpenRouter secret for LLM analysis:

```text
OPENROUTER_API_KEY=${{ secrets.OPENROUTER_API_KEY }}
LLM_MODEL=openrouter/free
```

The pull request number is supplied through:

```text
PR_NUMBER=${{ github.event.pull_request.number }}
```

### PR data and safety limits

The DevOps reviewer limits the amount of data sent to the model:

- Up to five changed files are analyzed.
- Each file patch is truncated to a configured maximum size.
- Total current patch text is bounded.
- Historical context is bounded before it is placed in the prompt.

The reviewer is instructed to avoid style-only comments and speculation. If no confirmed issue is found, it returns:

```text
No significant issues found.
```

## 7. How RAG and DevOps Work Together

The PR reviewer uses the same project-memory pipeline as the chatbot, but its query is generated from the current PR diff.

```text
Pull request opened or synchronized
                |
                v
       Read changed files and patches
                |
                v
    Retrieve similar historical project context
                |
                v
       Combine PR changes and context
                |
                v
       Ask the reasoning model for review
                |
                v
       Post review as a GitHub comment
```

This integration allows PMI to compare a new change with the repository's own history instead of reviewing the patch in isolation.

The chatbot uses the same indexed repository knowledge interactively:

```text
Authenticated user question
                |
                v
       Plan deterministic or semantic query
                |
                +--> Exact lookup/list/navigation
                |
                +--> ChromaDB retrieval
                              |
                              v
                    Grounded reasoning response
```

The two interfaces therefore share:

- The collection process.
- The normalized knowledge documents.
- The embedding model.
- The ChromaDB index.
- The retrieval layer.
- The project-context grounding rules.

## 8. Repository Refresh Options

### Command-line refresh

From the project root:

```powershell
python -m src.pipeline
```

This runs all four preparation stages:

```text
1. Collect repository data
2. Build the knowledge base
3. Generate embeddings
4. Rebuild ChromaDB
```

### UI refresh

Authenticated users can select **Prepare Repository** in the Streamlit interface. The UI invokes the same preparation function and displays success or failure feedback.

### GitHub Actions refresh

Every configured PR event performs a fresh preparation inside the GitHub Actions runner before reviewing the PR. This keeps the review context aligned with the repository state available to the workflow.

## 9. Configuration and Secrets

The main local configuration values are:

```env
GITHUB_TOKEN=your_github_token
REPO_OWNER=owner_name
REPO_NAME=repository_name
OPENROUTER_API_KEY=your_openrouter_key
LLM_MODEL=openrouter/free
COOKIES_PASSWORD=long-random-cookie-secret
```

Secrets must not be committed to Git or placed in public documentation. GitHub Actions should use repository or environment secrets rather than hardcoded credentials.

## 10. Current Limitations and Operational Notes

- The project depends on valid GitHub credentials and repository access.
- A `404` from GitHub can mean that the owner/name is wrong or that the token cannot access a private repository.
- A `401` means the GitHub token is invalid, expired, or revoked.
- The first embedding run may download the sentence-transformers model and can take time.
- Semantic answers require a working OpenRouter API key and model configuration.
- The chatbot API must be running before the Streamlit UI can sign users in or send questions.
- The current PR workflow posts one generated analysis comment rather than a line-level review.
- The review is intentionally bounded to a limited number of files and a limited amount of patch/context text.
- The current checkout does not include a tracked automated test suite, so operational smoke testing is important.

## 11. End-to-End Summary

PMI connects GitHub, RAG, authentication, a web chatbot, and DevOps automation into one project-memory system:

```text
GitHub repository
      |
      v
Collection of commits, issues, PRs, and documentation
      |
      v
Structured knowledge documents
      |
      v
Embeddings and ChromaDB
      |
      +--------------------------+
      |                          |
      v                          v
Authenticated chatbot       GitHub Actions PR review
      |                          |
      v                          v
Exact or semantic query      PR diff plus historical context
      |                          |
      v                          v
Grounded answer              Confirmed-issue analysis
      |                          |
      +------------+-------------+
                   v
             Engineering knowledge
```

The result is a single repository-aware system that supports both interactive engineering questions and automated, history-aware pull request feedback.
