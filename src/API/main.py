from fastapi import FastAPI
from pydantic import BaseModel

from src.Retrieval.query import retrieve_documents
from src.Retrieval.context import build_context
from src.Reasoning.llm import generate_response


app = FastAPI(
    title="PMI API",
    description="Project Memory Intelligence API",
    version="1.0.0",
)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: str
    history: list[ChatMessage] = []


@app.post("/chat")
def chat(request: ChatRequest):
    results = retrieve_documents(
        request.question,
        n_results=3,
    )

    context = build_context(results)

    conversation_history = "\n".join(
        f"{message.role}: {message.content}"
        for message in request.history
    )

    prompt = f"""
You are PMI, an AI project assistant.

Answer the user's question using only the provided project context.
Do not invent project information.

CONVERSATION HISTORY:
{conversation_history}

PROJECT CONTEXT:
{context}

USER QUESTION:
{request.question}
"""

    answer = generate_response(prompt)

    return {
        "question": request.question,
        "answer": answer,
    }


@app.get("/")
def root():
    return {"message": "PMI API is running"}