import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize

nltk.download('punkt')

def _split_into_sentences(paragraph):
    sentences = sent_tokenize(paragraph)
    return sentences

def scrape_drug(id):
    pairs = []
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

                    pairs.append(
                        (header, content)
                    )
            else:
                print("No <ul> element found nested inside class='drug-label-sections'.")
    else:
        print("No elements with class='drug-label-sections' found.")
    
    return pairs

def chunk(index_name, product_id):
    try:
        create_pc_index(index_name)
    except Exception as e:
        if int(e.status) != 409:
            raise e

    pairs = scrape_drug(product_id)

    for pair in pairs:
        sentences = _split_into_sentences(pair[1])
        vectors = [embeddings.embedding for embeddings in create_embeddings(sentences)]

        for idx, vector in enumerate(vectors):
            print(
                (vector, sentences[idx])
            )
            insert_embedding(INDEX_NAME, "certolizumab", pair[0], vector, sentences[idx])