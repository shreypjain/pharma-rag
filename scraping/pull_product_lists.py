from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse, parse_qs

# Send a GET request to the URL
base = "https://dailymed.nlm.nih.gov"

def parse_drug_classes():
    product_pairs = []
    url = base + "/dailymed/browse-drug-classes.cfm?searchInput=&refine=fdaepc&vandf=All+Categories"
    response = requests.get(url)

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    # Find the <ul> element with id="double"
    ul_element = soup.find('ul', id='double')

    # Extract text from <li> tags within <ul>
    if ul_element:
        drug_classes = ul_element.find_all('li')
        for drug_class in drug_classes:
            a_tag = drug_class.find('a')
            search_url = base + a_tag.get('href')
            product_pairs.extend(parse_product_search(search_url))
    
    else:
        print("No <ul> element with id='double' found.")
    
    return product_pairs


def parse_product_search(search_url):
    product_pairs = []
    response = requests.get(search_url)

    search_page = BeautifulSoup(response.text, 'html.parser')

    div = search_page.find(class_="results")

    if not div:
        return []

    articles = div.find_all("article")

    for article in articles:
        header = article.find("h2")
        link = header.find("a")

        product_name = link.get_text(strip=True)
        product_id = parse_qs(urlparse(link.get("href")).query).get('setid', [None])[0]

        product_pairs.append((product_name, product_id))
    
    return product_pairs

def write_drugs_to_file(drugs, filename):
    with open(filename, 'w') as file:
        for drug in drugs:
            # Joining the elements of each tuple with a comma and writing to the file
            file.write(','.join(drug) + '\n')

def read_drugs_from_file(filename):
    drugs = []
    with open(filename, 'r') as file:
        for line in file:
            # Split each line into elements separated by commas
            drug_data = line.strip().split(',')
            # Assuming each line has two elements: name and ID
            if len(drug_data) == 2:
                drugs.append((drug_data[0], drug_data[1]))
            else:
                print("Error: Invalid line format:", line)
    return drugs

drugs = parse_drug_classes()
write_drugs_to_file(drugs, "drug_list.txt")
