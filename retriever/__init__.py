import json
from config import oai, pc
from generation import create_completions
from retriever.reranker import rerank_retrievals
import re

extract_alpha_chars = lambda text: ' '.join(re.findall(r'[a-zA-Z]+', text))

INTENT_CLASSIFICATION_SYSTEM_PROMPT = """
As a Large Language Model, your exclusive task is to perform intent classification on the given text. You are to scrutinize the content and context thoroughly, and categorize it exclusively into the options I will provide. 

Your output should be precise, strictly adhering to the provided classification options. Carry out this task promptly and accurately and use all parts of the user prompt to classify the prompt.

YOUR OUTPUT SHOULD ONLY BE ONE OF THE FOLLOWING OPTIONS. REFRAIN FROM GENERATING TEXT OUTSIDE OF THESE OPTIONS.

Do not add any notes in parenthesis. Do not mention latest information. Do not talk about what else you know. Do not ask how else you can help. Do not ask for new data or reports. ONLY generate one of the following strings:

"""

import datetime

# Function to print with human-readable time
def print_with_readable_time(message):
    current_time = datetime.datetime.now()
    print(f"[{current_time.strftime('%H:%M:%S')}] {message}")

def read_section_name_set():
    with open("./scraping/section_name_set.json", "r") as f:
        section_names = list(json.load(f)["sections"])
        if isinstance(section_names, list):
            return section_names
        else:
            raise Exception("Can't use a none list as section_names")

def create_embeddings(content):
    if isinstance(content, str) and content == '':
        return []
    if not isinstance(content, list):
        content = [content]
    if not len(content):
        return []
    try:
        response = oai.embeddings.create(
            input=content,
            model="text-embedding-3-small"
        )
    except Exception as e:
        print("THIS IS THE CONTENT THAT ERRORED:")
        print(content)
        raise e

    return response.data

def _create_intent_classification_prompt(options):
    ic_prompt = INTENT_CLASSIFICATION_SYSTEM_PROMPT

    newline_options = f"{''.join([option for option in options])}\n"

    ic_prompt += newline_options

    return ic_prompt


def intent_classification(prompt, options, *args, **kwargs):
    system_prompt = _create_intent_classification_prompt(options)

    print("Creating intent classification for the first go")

    try:
        classified_option = create_completions(prompt, system_prompt).content

        print(classified_option)

        while classified_option not in options:
            print("Creating intent classification again")
            classified_option = create_completions(prompt, system_prompt).content
    except Exception as e:
        raise e
    
    return classified_option

def _lev_dist(s1, s2):
    distances = [[0] * (len(s2) + 1) for _ in range(len(s1) + 1)]

    for i in range(len(s1) + 1):
        distances[i][0] = i
    for j in range(len(s2) + 1):
        distances[0][j] = j

    for i in range(1, len(s1) + 1):
        for j in range(1, len(s2) + 1):
            if s1[i - 1] == s2[j - 1]:
                substitution_cost = 0
            else:
                substitution_cost = 1
            distances[i][j] = min(
                distances[i - 1][j] + 1,  # deletion
                distances[i][j - 1] + 1,  # insertion
                distances[i - 1][j - 1] + substitution_cost  # substitution
            )

    return distances[-1][-1]

def filter_retrievals_by_lev_distance(retrievals):
    filtered_retrievals = []

    try:
        for i in range(len(retrievals)):
            retrieval_i = retrievals[i]
            text_i = retrieval_i

            print('here')
            
            is_unique = True
            
            for j in range(i + 1, len(retrievals)):
                retrieval_j = retrievals[j]
                text_j = retrieval_j
                
                levenshtein_distance = _lev_dist(text_i, text_j)
                text_length = max(len(text_i), len(text_j))
                lev_ratio = levenshtein_distance / text_length

                print('HERE')
                
                # Check if the ratio exceeds the threshold
                if lev_ratio <= 0.06:
                    is_unique = False
                    break
            
            if is_unique:
                filtered_retrievals.append(retrieval_i)
    except Exception as e:
        raise e
        
    return filtered_retrievals

def retrieve_from_query(user_prompt, index_name, *args, **kwargs):
    index = pc.Index(index_name)

    print_with_readable_time("Creating Query Embeddings")

    try:
        query_embeddings = create_embeddings(
            user_prompt
        )[0].embedding
    except Exception as e:
        raise e

    print_with_readable_time("Doing intent classification")

    section_name = intent_classification(user_prompt, read_section_name_set())

    print_with_readable_time("Querying top k documents")
    try:
        retrievals = index.query(
            vector=query_embeddings,
            top_k=5,
            include_values=True,
            include_metadata=True,
            # TODO: add filtration by product_name
            # filter={"section_name": { "$eq": extract_alpha_chars(section_name) }}
        )

        chunks = retrievals.matches

        print_with_readable_time(chunks[0]["metadata"])

        # FAILED experiment – took way too long to actually run through lev_distance (n^4 time)
        # retrievals = filter_retrievals_by_lev_distance([chunk["metadata"]["text"] for chunk in chunks])

        print_with_readable_time("Reranking chunks")

        retrievals = rerank_retrievals(user_prompt, [(chunk["metadata"]["text"], chunk["metadata"]["product_name"]) for chunk in chunks], top_k=3)

        return retrievals
    except Exception as e:
        print("Issue with the user prompt: ", user_prompt)
        raise e