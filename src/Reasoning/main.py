from src.Retrieval.query import retrieve_documents
from src.Retrieval.context import build_context
from src.Reasoning.prompt import build_prompt
from src.Reasoning.llm import generate_response


def answer_question(question: str, n_results=3):
    results = retrieve_documents(
        question,
        n_results=n_results,
    )

    context = build_context(results)

    prompt = build_prompt(
        question,
        context,
    )

    answer = generate_response(prompt)

    return answer


def main():
    question = input("Ask a question: ")

    answer = answer_question(question)

    print("\nAnswer:\n")
    print(answer)


if __name__ == "__main__":
    main()