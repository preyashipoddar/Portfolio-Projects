import os
from openai import OpenAI
from database import get_connection
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def embed_query(query: str) -> list:
    response = client.embeddings.create(
        input=query,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def search_contract(doc_id: str, query: str, top_k: int = 5) -> list:
    query_embedding = embed_query(query)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT chunk_text
        FROM contract_chunks
        WHERE document_id = %s
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """, (doc_id, str(query_embedding), top_k))
    results = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return results

if __name__ == "__main__":
    results = search_contract("lease_simple", "can the landlord enter the property")
    for i, chunk in enumerate(results, 1):
        print(f"\n--- Chunk {i} ---")
        print(chunk)