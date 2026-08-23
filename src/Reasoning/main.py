from src.Reasoning.llm import generate_response
from src.Reasoning.prompt import build_prompt
from src.Retrieval.main import retrieve_context


def answer_question(question: str, n_results: int = 3) -> str:
    context = retrieve_context(question, n_results=n_results)
    if not context:
        return "I couldn't find relevant project context for that question."
    return generate_response(build_prompt(question, context))


def main():
    question = input("Ask a question: ").strip()
    print("\nAnswer:\n")
    print(answer_question(question))


if __name__ == "__main__":
    main()
