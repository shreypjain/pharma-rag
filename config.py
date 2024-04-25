import os
from dotenv import load_dotenv

from openai import OpenAI
from pinecone import Pinecone

load_dotenv()

oai = OpenAI(api_key=os.getenv("OAI_KEY"))
pc = Pinecone(api_key=os.getenv("PC_KEY"))

INDEX_NAME = "drug-information"