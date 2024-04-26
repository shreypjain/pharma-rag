from config import oai
import re

RERANK_PROMPT = lambda query, chunks, extra_information = "": f'''
<s>[INST] <<SYS>>
The following are pieces of information about drug products related to query: { query }

{extra_information}

{
    ''.join(
        [
            f"[{idx}]: {chunk}" for idx, chunk in enumerate(chunks)
        ]
    )
}
<</SYS>>
Your task is to rank these products based on their relevance to the query.
Use the following format to rank the products USING ONLY THEIR CORRESPONDING NUMBER and don't use anything else. Do not use the text associated with the number from the original input. As an example, your output should look like this:

3,7,4,5,9,6,8,2,1,10

And repeat this until all of the product names and text relating to product have been written out in this list.
Do not use any letters or words in your generation, only use numbers and commas, and stop once complete. Your response needs to be exactly {len(chunks)} numbers long WITH ONLY commas seperating each number. [/INST]
'''

def _convert_to_list_ints(input_string):
    return [int(num) for num in input_string.split(',')]

def validate_and_convert(input_string):
    pattern = r'^\d+(,\d+)*$'

    if re.match(pattern, input_string):
        return _convert_to_list_ints(input_string)
    else:
        print("Invalid input string format")
        return None

def reorder_retrievals(retrievals, reranked_index_list):
    # Need the same size list to make this happen
    if len(retrievals) != len(reranked_index_list):
        print("Error: Lengths of retrievals and reranked_index_list are not the same")
        return None
    
    # Same length list of retrievals
    reordered_retrievals = [None] * len(retrievals)

    for i, index in enumerate(reranked_index_list):
        reordered_retrievals[index] = retrievals[i]

    return reordered_retrievals

def create_rerank_completion(prompt, temperature, *args, **kwargs):
    completion = oai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        *args,
        **kwargs
    )

    return completion.choices[0].message.content


def rerank_retrievals(query, retrievals, *args, **kwargs):
    prompt = RERANK_PROMPT(query, retrievals)

    raw_indices = create_rerank_completion(prompt, 0.05, *args, **kwargs)

    reranked_indices = validate_and_convert(raw_indices)

    while not reranked_indices or len(reranked_indices) != len(retrievals):
        reranked_indices = validate_and_convert(create_rerank_completion(prompt, 0.05, *args, **kwargs))

    reranked_retrievals = reorder_retrievals(retrievals, reranked_indices)

    return reranked_retrievals
