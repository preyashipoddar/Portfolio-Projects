import os
import fitz
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI
from database import get_connection
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_text(pdf_path: str) -> str:
    try:
        doc = fitz.open(pdf_path)
        text = " ".join([page.get_text() for page in doc])
        if not text.strip():
            raise ValueError("No text extracted — this may be a scanned image PDF.")
        return text
    except Exception as e:
        raise RuntimeError(f"Failed to parse PDF: {e}")

def chunk_text(text: str) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    return splitter.split_text(text)

def embed_chunks(chunks: list) -> list:
    response = client.embeddings.create(
        input=chunks,
        model="text-embedding-3-small"
    )
    return [item.embedding for item in response.data]

def store_chunks(doc_id: str, chunks: list, embeddings: list):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM contract_chunks WHERE document_id = %s", (doc_id,))
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        cur.execute(
            "INSERT INTO contract_chunks (document_id, chunk_text, chunk_index, embedding) VALUES (%s, %s, %s, %s::vector)",
            (doc_id, chunk, i, str(embedding))
        )
    conn.commit()
    cur.close()
    conn.close()

def ingest_pdf(pdf_path: str, doc_id: str):
    print(f"Extracting text from {pdf_path}...")
    text = extract_text(pdf_path)
    print(f"Splitting into chunks...")
    chunks = chunk_text(text)
    print(f"Embedding {len(chunks)} chunks...")
    embeddings = embed_chunks(chunks)
    print(f"Storing in pgvector...")
    store_chunks(doc_id, chunks, embeddings)
    print(f"Done. {len(chunks)} chunks stored for document '{doc_id}'.")

if __name__ == "__main__":
    ingest_pdf("contracts/lease_simple.pdf", "lease_simple")