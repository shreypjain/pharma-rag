from pinecone import ServerlessSpec
from config import pc
import uuid

def create_pc_index(name):
    pc.create_index(
        name=name,
        dimension=1536, # OpenAI small model's dimensionality
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )

def insert_embedding(name, product_name, section_name, embedding, text):
    index = pc.Index(name)

    try:
        row = index.upsert(
            vectors=[
                {
                    "id": str(uuid.uuid4()),
                    "values": embedding,
                    "metadata": {
                        "product_name": product_name,
                        "section_name": str(section_name),
                        "text": text
                    }
                },
            ]
        )
    except Exception as e:
        raise e

    return row