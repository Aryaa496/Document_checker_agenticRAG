# Agentic RAG Compliance Checker

A self-correcting Retrieval-Augmented Generation (RAG) system that answers questions about UK Skilled Worker and Graduate visa rules — and measurably reduces hallucination on questions it can't actually answer, compared to a standard single-pass RAG pipeline.

Built on real UK Immigration Rules (Appendix Skilled Worker, Appendix Graduate), with a hand-labelled 71-question benchmark used to measure the difference between a baseline RAG system and an agentic, self-correcting one.

---

## The finding

| | Baseline RAG | Agentic RAG |
|---|---|---|
| **Overall accuracy** | 56/71 (79%) | **62/71 (87%)** |
| Answerable questions | 28/28 (100%) | 28/28 (100%) |
| Synthesis questions (require combining rules) | **12/18 (67%)** | 11/18 (61%) |
| Unanswerable / trick questions | 16/25 (64%) | **23/25 (92%)** |

Adding a self-correction loop (retrieve → judge sufficiency → rewrite query → retry) improved overall accuracy by 8 points, driven almost entirely by a large improvement in correctly declining to answer questions the rulebook doesn't cover. That improvement came at a small cost: the agentic system was slightly *more* likely to abstain on hard-but-answerable synthesis questions than the baseline.

Both systems independently made the same factual error on one question — confusing a salary figure from the settlement section with one from the initial application section — suggesting a shared retrieval blind spot rather than a generation-only problem.

**In short: self-correction is a real, measurable win against hallucination, but it's a tradeoff, not a free upgrade — added caution improves safety on genuinely unanswerable questions but costs some recall on hard, legitimately answerable ones.**

---

## Architecture

```
Rulebook (scraped, deduplicated gov.uk text)
        │
        ▼
  Chunking (LangChain RecursiveCharacterTextSplitter, ~500 char chunks)
        │
        ▼
  Embedding (BAAI/bge-small-en-v1.5, local, open-source — no API cost)
        │
        ▼
  Vector storage (Pinecone)
        │
        ├──► Baseline: single retrieve → generate pass
        │
        └──► Agentic (LangGraph):
                 retrieve → judge sufficiency → [insufficient] → rewrite query → retrieve (loop, max 3 attempts)
                                              → [sufficient] → generate answer
```

**Stack:** LangChain (loading/chunking) · Hugging Face BGE (embeddings, local) · Pinecone (vector store) · LangGraph (agentic orchestration) · Groq-hosted Llama/GPT-OSS (generation) · Pydantic (structured output) · Streamlit (frontend)

### Why an agentic loop at all?

A standard RAG pipeline retrieves once and answers — even if what it retrieved doesn't actually contain the answer. This project adds a **judge** step: after retrieving, the system asks itself "is this context actually sufficient to answer the question?" If not, it rewrites the search query and tries again (up to 3 attempts) before honestly saying it doesn't know, rather than guessing.

---

## Document-level compliance checker

The same engine is extended into a document checker: given a job offer letter, it extracts individual checkable claims (salary, SOC code, sponsor rating, etc.), cross-references each against the rulebook using the agentic engine, and returns a structured, schema-enforced verdict (`COMPLIANT` / `NON_COMPLIANT` / `UNCLEAR`) with the cited rule and confidence — surfaced through a Streamlit frontend.

**Key design decision:** each clause is checked *with the full document as context*, not in isolation. Checking clauses independently (e.g. "salary: £38,000" with no other context) caused the system to correctly, but unhelpfully, mark almost everything `UNCLEAR` — because most individual facts (salary, SOC code, sponsor rating) are only checkable in combination with each other, not alone.

---

## Known limitations

These were found through testing, not assumed — each is a specific, reproducible case:

- **Shared rulebook confusion:** both baseline and agentic systems confused the initial-application salary threshold (£41,700) with the settlement salary threshold (£31,300) on the same question — a retrieval-layer issue, not something the agentic loop alone fixes.
- **Over-caution on synthesis questions:** the self-correction loop occasionally abstains on questions that genuinely have an answer, when the judge is too strict about what counts as "sufficient" context.
- **Query-rewrite drift (fixed):** an early version of the query-rewriter occasionally hallucinated jurisdiction — rewriting a UK-specific query into US H-1B visa terminology. Fixed by explicitly anchoring the rewrite prompt to the UK immigration domain.
- **Realistic documents are often under-specified:** a genuine early-stage recruiter offer letter (tested against a real example) lacks the SOC code and sponsor detail needed to check compliance at all — the system correctly returns `UNCLEAR` rather than guessing, but this means the tool is best suited to formal sponsorship documentation (e.g. Certificates of Sponsorship), not casual offer letters.

---

## Evaluation methodology

- **71 hand-written test questions** across three categories: directly answerable (28), requiring synthesis across multiple rule sections (18), and deliberately unanswerable or "trick" questions not covered by the rulebook (25) — including a few genuinely answerable questions disguised as trick questions, to check the system doesn't over-abstain reflexively.
- Both systems run against the identical question set, identical underlying rulebook, and identical LLM (`openai/gpt-oss-20b` via Groq).
- Every answer manually checked against a pre-written expected answer — not just an automated keyword match for "I don't know," which only measures abstention, not correctness.

---

## Project structure

```
compliance-checker/
├── data/rulebook/              # Scraped, deduplicated UK Immigration Rules text
├── RAG/                        # Baseline RAG pipeline + evaluation
│   ├── chunking.py
│   ├── embedding.py
│   ├── retrieval.py
│   └── baseline_evaluate.py
├── Agentic/                    # Self-correcting agentic RAG + document checker
│   ├── looping.py              # LangGraph retrieve→judge→rewrite→answer loop
│   ├── document_checker.py     # Clause extraction + structured compliance checking
│   ├── app.py                  # Streamlit frontend
│   ├── agentic_evaluate.py
│   └── test_job_offers.py      # Realistic test documents
├── test_questions.py           # 71-question evaluation set
└── compare_results.py          # Baseline vs. agentic comparison
```

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file with:
```
PINECONE_API_KEY=your-key
GROQ_API_KEY=your-key
```

Run the baseline and agentic evaluations, then compare:
```bash
cd RAG && python baseline_evaluate.py
cd ../Agentic && python agentic_evaluate.py
cd .. && python compare_results.py
```

Run the frontend:
```bash
cd Agentic && python -m streamlit run app.py
```

---

## What's next

- Expand the rulebook to cover the Student route, to close the gap on Student-visa-while-studying questions
- Reduce over-caution on synthesis questions by loosening the sufficiency-judge threshold or increasing retrieved context (`k`)
- Add a shared, cross-checking step for salary figures specifically, to catch the settlement/application threshold confusion both systems share
