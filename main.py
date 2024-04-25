from retriever import retrieve_from_query
from generation import generate_with_retrieval
from config import INDEX_NAME
from scraping import chunk
from scraping.pull_product_lists import parse_drug_classes, read_drugs_from_file

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

# chunk(INDEX_NAME, "product_name", "bdbf5ad4-86f2-4e9c-a51a-fb0c7220c480")

all_drugs = read_drugs_from_file("./scraping/drug_list.txt")

for drug in all_drugs:
    product_name, product_id = drug

    chunk(INDEX_NAME, product_name, product_id)
main()
