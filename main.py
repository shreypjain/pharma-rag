from retriever import retrieve_from_query
from generation import generate_with_retrieval

def main():
    user_prompt = input("User prompt: ")

    retrievals = retrieve_from_query(
        user_prompt,
        INDEX_NAME
    )

    generation = generate_with_retrieval(
        retrievals,
        user_prompt,
        temperature=0.3,
        max_tokens=4096
    )

    print(generation)
