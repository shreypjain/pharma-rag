import re
import requests
from bs4 import BeautifulSoup
import json
import nltk
import tiktoken
from nltk.tokenize import sent_tokenize
from retriever import create_embeddings
from retriever.vdb import create_pc_index, insert_embedding

nltk.download('punkt')
encoding = tiktoken.get_encoding("cl100k_base")
        
def write_section_name_set(new_section_names):
    # Get rid of duplicates
    new_section_names = list(set(new_section_names))

    with open("./scraping/section_name_set.json", "w") as f:
        if not isinstance(new_section_names, list):
            return
        
        json.dump({
            "sections": new_section_names
        }, f)

def _split_into_sentences(paragraph):
    sentences = sent_tokenize(paragraph)
    return sentences

def split_into_4k_tokens(text):
    splits_idx = 0
    counted_token_length = 0

    MAX_CONTENT_LENGTH = 4096

    splits = []

    sentences = _split_into_sentences(text)

    for _, sentence in enumerate(sentences):
        sentence_w_space = " " + sentence
        tokens_in_sentence = len(encoding.encode(sentence_w_space))

        if splits_idx == 0 or counted_token_length + tokens_in_sentence > MAX_CONTENT_LENGTH:
            splits.append(sentence_w_space)  # Start a new split
            splits_idx += 1
            counted_token_length = tokens_in_sentence  # Reset the count for the new split
        else:
            splits[splits_idx - 1] += sentence_w_space  # Add the sentence to the current split
            counted_token_length += tokens_in_sentence  # Update the total token count
        
    return splits


def scrape_drug(id):
    pairs, section_names = [], []
    # URL of the webpage to scrape
    url = f"https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid={id}##"

    # Send a GET request to the URL
    response = requests.get(url)

    # Parse the HTML content of the webpage using BeautifulSoup
    soup = BeautifulSoup(response.text.replace('\n', ' '), "html.parser")

    # Find all elements with class="drug-label-sections"
    drug_label_sections = soup.find_all(class_="drug-label-sections")

    # Check if any elements are found
    if drug_label_sections:
        # Iterate over each element with class="drug-label-sections"
        for section in drug_label_sections:
            # Find the nested <ul> element
            nested_ul = section.find("ul")

            lis = nested_ul.findChildren("li", recursive=False)
            
            # Check if a <ul> element is found
            if nested_ul:
                for idx, li in enumerate(lis, start=1):
                    header = li.find(id=f"anch_dj_dj-dj_{idx}").get_text(strip=True)
                    content = li.find(class_=re.compile("toggle-content")).get_text(strip=True)

                    section_names.append(header)

                    pairs.append(
                        (header, content)
                    )
            else:
                print("No <ul> element found nested inside class='drug-label-sections'.")
    else:
        print("No elements with class='drug-label-sections' found.")

    write_section_name_set(section_names)
    
    return pairs

def write_to_json(product_name, product_id):
    product_name = product_name.replace(" ", "_").replace("\n", "")
    
    with open(f"./scraping/drug-information/{product_name}.json", 'w+') as file:
        pairs = scrape_drug(product_id)
        drug_json = {
            "name": product_name,
            "sections": []
        }

        # Iterate through pairs and add to sections list
        for header, content in pairs:
            section = {"header": header, "content": content}
            drug_json["sections"].append(section)

        json.dump(drug_json, file)
    
    return drug_json, True


def chunk(index_name, product_name, product_id):
    try:
        print("Checking / Creating Index")
        create_pc_index(index_name)
    except Exception as e:
        if int(e.status) != 409:
            raise e

    pairs = scrape_drug(product_id)
    print(pairs)

    for pair in pairs:
        print("Splitting into 4k tokens")
        paragraphs = split_into_4k_tokens(pair[1])
        print("Generating Vectors")
        vectors = [embeddings.embedding for embeddings in create_embeddings(paragraphs)]

        for idx, vector in enumerate(vectors):
            print(
                (vector, paragraphs[idx])
            )
            # TODO: Replace second parameter with parsed out product name
            insert_embedding(index_name, product_name, pair[0], vector, paragraphs[idx])