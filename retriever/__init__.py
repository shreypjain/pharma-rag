from config import oai
from generation import create_completions

def create_embeddings(content):
    if not isinstance(content, list):
        content = [content]
    response = oai.embeddings.create(
        input=content,
        model="text-embedding-3-small"
    )

    return response.data

def intent_classification(prompt, options, *args, **kwargs):
    classified_option = create_completions(prompt, "system prompt")

    while classified_message not in options:
        classified_option = create_completions(prompt, "system prompt")
    
    return classified_option

def retrieve_from_query(user_prompt, index_name, *args, **kwargs):
    index = pc.Index(index_name)

    query_embeddings = create_embeddings(
        query
    )

    # TODO: Replace blank array with full vocab set
    section_name = intent_classification(query, [])

    retrievals = index.query(
        vector=query_embeddings,
        top_k=5,
        include_values=True,
        include_metadata=True,
        filter={"section_name": { "$eq": section_name }}
    )

    # TODO: Set up a reranking step

    return retrievals.matches