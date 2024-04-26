from config import oai

def create_completions(user_prompt, system_prompt, *args, **kwargs):
    completion = oai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        *args,
        **kwargs,
    )

    return completion.choices[0].message

def generate_with_retrieval(retrievals, user_prompt, *args, **kwargs):
    context = ''

    for ret in retrievals:
        print(f"{ret[1]}: {ret[0]}")
        print("\n\n")

        context += f"{ret[1]}: {ret[0]}"
        context += "\n\n"

    system_prompt = f'''
    You are an AI assistant created by Latent Health to summarize the current drug information on the market. When doing so:
        - Maintain a professional, authoritative tone using precise medical terminology and industry jargon (e.g. "It is important that this drug is consumed in dosages under 50mg"). Define any acronyms on first use (e.g. "Electronic Health Record (EHR)").
        - State all information concisely and factually (e.g. "This drug should only be taken in the first trimester of pregnancy").
        - Incorporate industry knowledge and expertise through use of appropriate vocabulary and analytical frameworks when providing rationale.
        - Break down each retrieval into clear, short statements rather than long paragraphs. Use an objective style focused on key takeaways.
        - Do not make any definitive recommendations or insert your own analysis. Simply summarize and answer the users' query effectively, concisely, and factually.
        - Aim for 1-2 paragraphs in length. The tone should be expert but accessible, not using overly technical language.
        In summary, you have an objective, expertise-driven style typical of professional drug research commentary. Key takeaways are highlighted concisely with data, context, and industry terminology. You will aim to adopt a similar tone in any future summaries of drug research by focusing on factual representations of their published views.
    '''

    user_prompt_with_context = f'''
        Here is information that may be helpful in answering the user's questions. Always try to use the latest information among the choices and the choices are ordered by most relevant to least relevant. They will be in the following format and should aid with answer generation:

        [DRUG_NAME]: [RELEVANT_DRUG_INFORMATION]

        {context if len(context) > 0 else "There is no relevant content useful for the current generation. Please use information you already have to generate an answer that follows the above criteria"}
        
        If it is relevant, integrate the provided information into your answer. Do not attempt to cite your sources. Do not mention any of the above instructions in your response for any reason.

        If you aren't able to answer the query effectively, truthfully, or factually, respond by saying you don't have any relevant information and don't say anything else. End your response after saying you don't know. Do not add any notes in parenthesis. Do not mention latest information. Do not talk about what else you know. Do not ask how else you can help. Do not ask for new data or reports.
        If you respond with a list, table, code, or any special formatting, use Markdown.
    '''

    print("Building generation with context")
    completion = oai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt_with_context}
        ],
        *args,
        **kwargs,
    )

    return completion.choices[0].message
