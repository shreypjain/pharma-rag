import json
from config import oai, INDEX_NAME
from generation import generate_with_retrieval
from retriever import retrieve_from_query

def ret_and_gen(user_prompt):
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

        return generation.content, retrievals
    except Exception as e:
        raise e

def create_triplets():
    sys_prompt = """You are a medical student looking to ask questions about specific drugs to your textbook. Use your existing knowledge of the following drugs to create a set of 5 questions about these drugs.
    Make sure that you do not add any notes in parenthesis. Do not mention latest information. Do not talk about what else you know. Do not ask how else you can help. Do not ask for new data or reports.

    Only respond with 5 questions seperated by a new line.

    These questions will be used in creating answers generated on a set of information from the NIH DailyMed documentation on drugs. 
    """

    messages = [
        {
            "role": "system",
            "content": sys_prompt
        }
    ]

    questions = []
    drugs = [
        ("NITISINONE capsule", "437868f5-1c9e-4b0f-8a03-77df8ac0900d"),
        ("COSYNTROPIN injection, powder, lyophilized, for solution","1342169c-e214-4f22-8363-1fd45b85d1e8"),
        ("BELRAPZO (bendamustine hydrochloride) injection","9759a4ae-82ca-40cf-9c02-e1cadb21cbdc"),
        ("AXIRON (testosterone) solution","3b40e56a-51bb-4357-8861-325bb1195049"),
        ("ADVIL COLD AND SINUS (ibuprofen and pseudoephedrine hydrochloride) tablet,coated","fac22a47-f0de-4505-fd8a-768430cda0c1")
    ]

    for product_name, _ in drugs:
        print(f"Building completions for {product_name}")
        completions = oai.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages + [{"role": "user", "content": product_name}]
        )

        content = completions.choices[0].message.content
        dqs = content.split('\n')[:5]

        questions.extend(dqs)
    
    triplets = []

    for question in questions:
        generation, retrievals = ret_and_gen(question)

        print(f"Appending triplets for this question:   {question}")

        triplets.append(
            {
                "question": question,
                "retrievals": retrievals,
                "generation": generation,
            }
        )
    
    with open("triplets.json", "w") as json_file:
        json.dump(triplets, json_file, indent=4)

create_triplets()
