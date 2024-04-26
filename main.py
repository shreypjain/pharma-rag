from retriever import retrieve_from_query
from generation import generate_with_retrieval
from config import INDEX_NAME

import gradio as gr

def main(user_prompt):
    try:
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

        return generation.content
    except Exception as e:
        raise e

# chunk(INDEX_NAME, "product_name", "bdbf5ad4-86f2-4e9c-a51a-fb0c7220c480")

# all_drugs = read_drugs_from_file("./scraping/drug_list.txt")

# for drug in all_drugs:
#     product_name, product_id = drug

#     write_to_json(product_name, product_id)
    # chunk(INDEX_NAME, product_name, product_id)

interface = gr.Interface(
    fn=main,
    inputs=["text"],
    outputs=["text"]
)

interface.launch(share=True)

