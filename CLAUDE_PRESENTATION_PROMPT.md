# Prompt for Claude: Generate a PMI Project Presentation

Create a polished technical presentation for the project below.

## Project

**Name:** PMI (Project Memory Intelligence)

PMI is a GitHub-centric project-memory and DevOps assistant. It collects repository activity and documentation, converts the data into structured knowledge, generates embeddings, stores the knowledge in ChromaDB, and uses retrieval plus language-model reasoning to answer project questions. It also performs automated Pull Request analysis through GitHub Actions.

The presentation audience is a mixed technical audience: software engineers, DevOps engineers, technical managers, and project reviewers. Assume they understand GitHub and basic AI concepts, but do not assume they know the internal codebase.

## Presentation Goal

Explain:

- The problem PMI solves
- Why ordinary chat with an LLM is insufficient for project-specific knowledge
- PMI's end-to-end architecture and data flow
- How retrieval and deterministic operations work together
- How the chatbot and automated PR review workflows are used
- The main design decisions, security considerations, and current limitations
- The value and possible future direction of the project

The presentation should feel like a real product and engineering presentation, not a generic AI slideshow. Use precise claims grounded in the project description below. Do not invent metrics, users, production deployments, benchmarks, or capabilities that are not stated.

## Required Slide Structure

Create 12 to 14 slides. For every slide, provide:

1. Slide title
2. A concise subtitle or central message
3. The exact on-slide text, limited to short bullets and labels
4. A visual recommendation
5. Speaker notes with a clear explanation of the slide
6. A transition sentence to the next slide

Use this structure:

### Slide 1: Title

Introduce PMI as a project-memory and DevOps assistant. Use the tagline:

> Turn repository history into usable engineering knowledge.

Show a visual suggestion that combines a GitHub repository, a searchable knowledge base, and an assistant interface.

### Slide 2: The Problem

Explain why project knowledge is difficult to use:

- Important context is distributed across commits, issues, pull requests, and documentation.
- Engineers lose time searching across disconnected sources.
- Generic LLMs do not automatically know the repository's history.
- Answers must be grounded in project evidence.

### Slide 3: PMI's Solution

Show PMI as a system that turns repository data into searchable, contextual answers and automated engineering feedback.

Clearly distinguish the two main experiences:

- Conversational project assistant
- Automated Pull Request reviewer

### Slide 4: End-to-End Architecture

Create a clear architecture diagram with these stages:

1. GitHub repository
2. Data collection
3. Knowledge extraction
4. Embedding generation
5. ChromaDB vector index
6. Retrieval and deterministic query operations
7. Reasoning model
8. FastAPI backend and Streamlit UI
9. GitHub Actions PR review

Make the data flow directional and easy to follow. Explain that the preparation pipeline rebuilds the vector database so stale records do not remain after a refresh.

### Slide 5: Data Collection and Knowledge Extraction

Explain that PMI collects:

- Commits
- Issues
- Pull requests
- Markdown documentation

Then explain that these sources are converted into structured knowledge documents with stable IDs, entity types, human-readable text, and metadata.

Mention the canonical ID examples:

- `commit_<7-char-sha>`
- `pr_<number>`
- `issue_<number>`
- `doc_<filename-with-dots-replaced>`

### Slide 6: Embeddings and ChromaDB

Explain the role of embeddings and semantic search in plain language:

- Project content is represented as vectors.
- A question is compared with indexed project knowledge.
- The most relevant records become context for the answer.
- ChromaDB stores the searchable vector collection.

Do not claim that vector similarity alone answers every question.

### Slide 7: Retrieval Plus Deterministic Operations

Highlight PMI's key design decision: use exact operations when the answer is structured and semantic retrieval when interpretation is needed.

Show these deterministic operations:

- `get`
- `list`
- `previous`
- `next`
- `list_files`

Explain the active-reference example:

> Tell me about PR #15 -> What files did it change? -> What was the previous PR?

Clarify that `previous` and `next` do not replace the active reference with the returned record.

### Slide 8: Reasoning and Grounded Answers

Explain the reasoning stage:

- Retrieval supplies project context.
- The model uses that context to answer semantic questions.
- The system instructs the model not to invent project facts.
- Repository content is treated as untrusted data, so instructions embedded in project content must not be followed as model instructions.

Use a simple context -> prompt -> answer visual.

### Slide 9: Chatbot Experience

Explain the user workflow:

1. A user signs up or signs in.
2. The user asks a project question in the Streamlit UI.
3. The UI sends the request to the FastAPI API.
4. PMI retrieves the relevant project records.
5. The answer is returned with the conversation's active reference.
6. Chat sessions and messages are persisted.

Mention that the UI uses persistent authentication cookies and the API exposes the `/chat` endpoint.

### Slide 10: Automated Pull Request Review

Explain the GitHub Actions workflow:

1. A pull request is opened or synchronized.
2. The workflow checks out the repository.
3. Dependencies are installed.
4. PMI collects and processes repository data.
5. Embeddings and the vector database are rebuilt.
6. The changed files and historical context are analyzed.
7. PMI posts an analysis comment back to the pull request.

Show this as a CI/CD sequence diagram. Do not describe it as an autonomous code-merging system; it produces review feedback.

### Slide 11: Technology Stack

Present the technologies by responsibility, using only technologies represented by the project:

- Python
- FastAPI
- Streamlit
- GitHub Actions
- ChromaDB
- PyTorch and Transformers/PEFT for local model support
- Hugging Face model infrastructure
- SQLAlchemy/database layer for chat persistence

Where implementation details vary by execution path, explain that the interactive API and CI workflow can use different model configuration approaches. Do not imply that every environment uses the same model backend.

### Slide 12: Security and Reliability

Cover the following concrete practices and concerns:

- Secrets and tokens are supplied through environment variables or GitHub Secrets.
- `.env` files and tokens must not be committed.
- Repository content is untrusted input to the reasoning model.
- Authentication protects the chat application and API routes.
- The vector database is rebuilt during preparation to reduce stale-data risk.
- Model loading can be resource-intensive and depends on environment configuration.

Separate implemented protections from operational considerations.

### Slide 13: Current Status and Limitations

Be transparent:

- The repository preparation, retrieval, reasoning, API/UI, and PR-review paths are implemented.
- Phase 8 is not implemented and should not be presented as an existing feature.
- A valid environment requires configured credentials and dependencies.
- Model startup and inference may require substantial memory and time.
- Retrieval quality depends on the collected repository data and generated embeddings.
- The system should be evaluated with representative repositories and questions before production use.

Do not turn limitations into vague marketing language.

### Slide 14: Impact and Next Steps

Close with the practical value of PMI:

- Reduce time spent searching project history.
- Preserve institutional engineering context.
- Give developers repository-aware answers.
- Add historical context to Pull Request review.

Suggest realistic future work, clearly labeled as future work:

- Better evaluation datasets and answer-quality metrics
- More repository connectors and document formats
- Improved model serving and startup performance
- Richer PR review findings and traceable evidence
- Role-based access control and production deployment hardening

End with a concise closing message and three discussion questions.

## Visual and Design Direction

Use a modern engineering-product visual language:

- Dark charcoal or deep navy background with restrained cyan, green, and amber accents.
- Strong typography hierarchy and generous spacing.
- Consistent icons for GitHub, documents, vectors, databases, chat, and CI/CD.
- Use architecture diagrams, sequence diagrams, and small interface mockups instead of dense paragraphs.
- Keep each slide focused on one idea.
- Use a limited number of short bullets; put explanation in speaker notes.
- Avoid generic robot imagery, stock-photo clichés, decorative gradients, and unexplained buzzwords.
- Use code-style labels for API endpoints, commands, and canonical IDs.
- Make diagrams readable when projected in a room.

## Output Format

Return the presentation in this order:

1. A one-paragraph presentation concept
2. A slide-by-slide storyboard for all 14 slides
3. A complete visual style guide
4. Mermaid diagrams for the architecture and Pull Request workflow
5. Speaker notes for each slide
6. A final checklist confirming that the presentation:
   - Does not claim unimplemented functionality
   - Distinguishes deterministic retrieval from LLM reasoning
   - Explains both the chatbot and PR-review workflows
   - Mentions security and operational limitations
   - Avoids invented metrics or unsupported claims

If you generate an actual presentation file or slide code, preserve the same slide order and content requirements. Use the speaker notes as presenter notes rather than placing all explanatory text on the slides.
