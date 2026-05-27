````markdown
# PaperShield — AI Contract Risk Analyzer

PaperShield is a Retrieval-Augmented Generation (RAG) system that analyzes legal contracts and surfaces risky, one-sided, or unusual clauses with explainable, clause-grounded outputs.

You can upload a contract, ask questions grounded in the document, or run a full automated risk scan. The system is accessible via a CLI interface and an optional Streamlit UI.

---

## System Overview

PaperShield combines document retrieval, structured LLM outputs, and external legal validation to provide reliable contract analysis while minimizing hallucination and unsafe behavior.

---

## System Architecture

- **Ingestion:** PDFs parsed using PyMuPDF (`fitz`)
- **Chunking:** `RecursiveCharacterTextSplitter`
- **Retrieval:** Relevant clauses retrieved via semantic search (pgvector)
- **Generation:** Responses generated using OpenAI LLM (GPT-4o)
- **Validation:** Outputs validated using `jsonschema`

### Modes

- **Risk Scan**
  - Identifies and classifies risky clauses (High / Medium / Low)
  - Produces structured outputs with explanation, legal context, and recommendations

- **Ask Mode**
  - Answers user questions using retrieved clauses
  - Returns grounded responses with citations

---

## API Integrations

- **OpenAI API**
  - LLM reasoning and structured output generation
  - Embeddings for semantic retrieval

- **Tavily API**
  - External legal validation
  - Used for jurisdiction-specific context (e.g., California law)

---

## Interface

- **CLI Interface**
  - Built with `typer`
  - Primary interaction method

- **Streamlit UI (Optional)**
  - Interactive frontend for testing and demos
  - Directly calls backend logic (no API server required)

---

## Setup Instructions

### Prerequisites
- Python 3.10+
- Docker Desktop installed and running

---

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd capstone-project-ppoddar0101
````

---

### 2. Start the database

```bash
docker run -d --name papershield-db \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=papershield \
  -p 5432:5432 ankane/pgvector
```

If the container already exists:

```bash
docker start papershield-db
```

---

### 3. Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

---

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 5. Configure API keys

```bash
cp .env.example .env
```

Add your API keys to `.env`.

---

## Running the Application

### CLI Usage

Upload and index a contract:

```bash
python papershield.py upload contracts/lease.pdf
```

Ask a question:

```bash
python papershield.py ask lease "What is the late fee?"
```

Run a risk scan:

```bash
python papershield.py scan lease
```

---

### Streamlit UI (Optional)

Start the UI:

```bash
streamlit run ui.py
```

Then open the local URL (typically [http://localhost:8501](http://localhost:8501)).

---

## Features

### 1. Upload a Contract

* Extracts text from PDF
* Chunks and embeds content
* Stores vectors in pgvector

### 2. Ask Questions

* Natural language querying
* Returns structured output:

  * Answer
  * Cited clause
  * Section
  * Disclaimer

### 3. Risk Scan

* Full contract analysis using:

  * RAG (pgvector retrieval)
  * GPT-4o reasoning
  * Tavily web search
* Outputs:

  * Clause
  * Risk level
  * Plain English explanation
  * Legal context
  * Recommendation

---

## How It Works

1. **Upload**

   * PyMuPDF extracts text
   * LangChain splits into chunks (500 tokens, 50 overlap)
   * OpenAI embeddings generated
   * Stored in pgvector

2. **Retrieve**

   * Query embedded using same model
   * pgvector retrieves top-k similar chunks

3. **Agent**

   * GPT-4o processes retrieved context
   * Calls Tavily when external validation is needed
   * Produces structured JSON output

4. **Validate**

   * `jsonschema` enforces strict output format
   * Ensures consistency and reliability

---

## Evaluation Methodology

### Evaluation Metrics

| Metric                  | Definition                                      |
| ----------------------- | ----------------------------------------------- |
| **Answer Accuracy**     | Response correctly reflects the contract clause |
| **Citation Accuracy**   | Correct clause is cited as evidence             |
| **Consistency**         | Same answer across repeated runs                |
| **Abstention Accuracy** | Correctly indicates when information is missing |
| **Hallucination Rate**  | % of answers containing unsupported claims      |

---

### Quantitative Results

| Category          | Accuracy | Consistency | Notes                            |
| ----------------- | -------- | ----------- | -------------------------------- |
| Commercial Lease  | 80%      | 60%         | Risk classification inconsistent |
| Airbnb ToS        | 90%      | 85%         | Strong retrieval                 |
| Apple Terms       | 75%      | 65%         | Some conflicting interpretations |
| NDA               | 85%      | 70%         | Good uncertainty handling        |
| Residential Lease | 95%      | 90%         | Strong factual retrieval         |
| **Overall**       | **85%**  | **74%**     |                                  |

* **Hallucination Rate:** ~5–10%
* **Abstention Accuracy:** ~95%

---

### Key Findings

* Strong performance on **factual retrieval**
* Moderate inconsistency in **risk classification**
* Reliable **abstention behavior**
* Minimal hallucination, mostly in ambiguous legal interpretation

---

## Vulnerability Assessment

### Attack Success Rates

| Attack Type           | Model Resisted (%) | Outcome                         |
| --------------------- | ------------------ | ------------------------------- |
| Prompt Injection      | 100%               | Ignored malicious instructions  |
| Role Manipulation     | 100%               | Did not adopt unsafe personas   |
| Hallucination Forcing | 100%               | Refused to fabricate            |
| Nonsense Input        | 100%               | Correctly abstained             |
| Legal Advice Coercion | 100%               | Avoided definitive legal advice |

---

### Guardrails Observed

* **Instruction Hierarchy Enforcement**

  * Ignores attempts to override system instructions

* **Grounded Responses**

  * Outputs tied to retrieved clauses

* **Safe Abstention**

  * Indicates when information is missing

* **No Fabrication**

  * Refuses to generate unsupported claims or statutes

---

### Observed Weaknesses

* Inconsistent risk classification across runs
* Minor variation in clause interpretation
* Occasional vague phrasing instead of explicit refusal

---

## Conclusion

PaperShield demonstrates strong performance in clause-grounded retrieval and safe handling of adversarial inputs. While consistency in risk classification can be improved, the system is robust against prompt injection, avoids hallucination, and provides reliable, explainable outputs for legal document analysis.

---

## Notes on Architecture

* **Backend:** Python
* **Vector DB:** PostgreSQL with pgvector (Docker)
* **LLM:** GPT-4o
* **Embeddings:** text-embedding-3-small
* **Search Tool:** Tavily API
* **Orchestration:** LangChain LCEL
* **Validation:** jsonschema

The Streamlit UI directly imports:

* `ingest.py`
* `agent.py`
* `retrieve.py`

No separate API server is required.