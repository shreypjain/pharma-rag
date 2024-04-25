from config import oai, pc
from generation import create_completions
from scraping import read_section_name_set

INTENT_CLASSIFICATION_SYSTEM_PROMPT = """
As a Large Language Model, your exclusive task is to perform intent classification on the given text. You are to scrutinize the content and context thoroughly, and categorize it exclusively into the options I will provide. 

Your output should be precise, strictly adhering to the provided classification options. Carry out this task promptly and accurately and use all parts of the user prompt to classify the prompt.

YOUR OUTPUT SHOULD ONLY BE ONE OF THE FOLLOWING OPTIONS. REFRAIN FROM GENERATING TEXT OUTSIDE OF THESE OPTIONS.

Do not add any notes in parenthesis. Do not mention latest information. Do not talk about what else you know. Do not ask how else you can help. Do not ask for new data or reports. ONLY generate one of the following strings:

"""

def create_embeddings(content):
    if not isinstance(content, list):
        content = [content]
    response = oai.embeddings.create(
        input=content,
        model="text-embedding-3-small"
    )

    return response.data

def _create_intent_classification_prompt(options):
    ic_prompt = INTENT_CLASSIFICATION_SYSTEM_PROMPT

    newline_options = f"{''.join([option for option in options])}\n"

    ic_prompt += newline_options

    return ic_prompt


def intent_classification(prompt, options, *args, **kwargs):
    system_prompt = _create_intent_classification_prompt(options)

    classified_option = create_completions(prompt, system_prompt)

    while classified_option not in options:
        classified_option = create_completions(prompt, system_prompt)
    
    return classified_option

def retrieve_from_query(user_prompt, index_name, *args, **kwargs):
    index = pc.Index(index_name)

    query_embeddings = create_embeddings(
        user_prompt
    )

    # TODO: Replace blank array with full vocab set
    section_name = intent_classification(user_prompt, read_section_name_set())

    retrievals = index.query(
        vector=query_embeddings,
        top_k=5,
        include_values=True,
        include_metadata=True,
        filter={"section_name": { "$eq": section_name }}
    )

    # TODO: Set up a reranking step

    return retrievals.matches