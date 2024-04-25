from retriever import retrieve_from_query
from generation import generate_with_retrieval
from config import INDEX_NAME
from scraping import chunk

def main():
    try:
        user_prompt = input("User prompt: ")

        print("Doing retrieval")

        retrievals = retrieve_from_query(
            user_prompt,
            INDEX_NAME
        )

        print("Doing generation")

        generation = generate_with_retrieval(
            retrievals,
            user_prompt,
            temperature=0.3,
            max_tokens=4096
        )

        print("\n" + generation.content)
    except Exception as e:
        raise e

chunk(INDEX_NAME, "b4c2c9dc-a0bb-4d64-a667-a67ebe88392d")
# main()
