import typer
import os
import json
from dotenv import load_dotenv
from database import setup_database
from ingest import ingest_pdf
from agent import run_ask, run_scan

load_dotenv()
app = typer.Typer()

@app.command()
def upload(pdf_path: str, doc_id: str = None):
    """Upload and index a contract PDF."""
    if not doc_id:
        doc_id = os.path.basename(pdf_path).replace(".pdf", "")
    setup_database()
    ingest_pdf(pdf_path, doc_id)

@app.command()
def ask(doc_id: str, question: str):
    """Ask a question about an uploaded contract."""
    result = run_ask(doc_id, question)
    print(json.dumps(result, indent=2))

@app.command()
def scan(doc_id: str):
    """Run an automatic risk scan on an uploaded contract."""
    risks = run_scan(doc_id)
    if not risks:
        print("No significant risks detected.")
    else:
        print(f"\nFound {len(risks)} risk(s):\n")
        for i, risk in enumerate(risks, 1):
            print(f"Risk {i}: [{risk['risk_level'].upper()}] {risk['clause'][:80]}...")
            print(f"  {risk['plain_english']}\n")
    print(json.dumps(risks, indent=2))

if __name__ == "__main__":
    app()