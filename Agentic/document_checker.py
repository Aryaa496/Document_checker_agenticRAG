# document_checker.py

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Literal

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential

# IMPORT THE COMPILED LANGGRAPH APP AND LLM FROM LOOPING.PY
from looping import app as rag_app, llm

load_dotenv()


# ============================================================
# PYDANTIC SCHEMAS FOR STRUCTURED OUTPUTS
# ============================================================


class ExtractedClauses(BaseModel):
    clauses: List[str] = Field(
        description="List of single, self-contained factual statements from the document relevant to immigration eligibility."
    )


class ClauseAnalysis(BaseModel):
    status: Literal["COMPLIANT", "NON_COMPLIANT", "UNCLEAR"] = Field(
        description="Compliance status against UK visa rules."
    )
    applicable_requirement: str = Field(
        description="The specific rule, threshold, or option applied."
    )
    document_value: str = Field(
        description="The relevant value stated in the document."
    )
    required_value: str = Field(
        description="The applicable threshold or required value."
    )
    reason: str = Field(
        description="Concise explanation of the compliance decision."
    )
    rule: str = Field(description="The specific immigration rule reference used.")


# ============================================================
# TENACITY RETRY SAFEGUARD FOR STRUCTURED CALLS
# ============================================================


@retry(
    wait=wait_exponential(min=3, max=30),  # Wait 3s, 6s, 12s... up to 30s
    stop=stop_after_attempt(5),            # Retry up to 5 times
    reraise=True,
)
def safe_structured_invoke(structured_llm, prompt: str):
    """Safely invoke structured LLM calls with retry backoff for Groq 429 limits."""
    return structured_llm.invoke(prompt)


# ============================================================
# STEP 1: Extract checkable clauses
# ============================================================


def extract_clauses(document_text: str) -> List[str]:
    """Extract individual factual claims using LLM native structured output."""
    structured_llm = llm.with_structured_output(ExtractedClauses)

    prompt = f"""
Read the following job offer document.

Extract every individual factual claim that could be checked against
UK Skilled Worker or Graduate visa requirements.

Relevant claims may include:
- salary
- job title
- occupation/SOC code
- working hours
- sponsor details
- sponsorship status
- employment conditions
- visa route
- job duties
- start date
- qualification requirements
- other facts relevant to visa eligibility

Do not extract greetings, addresses, signatures, or generic wording.

Each claim must:
- be a single self-contained sentence
- contain only information stated in the document
- be independently checkable

Document:
{document_text}
"""

    try:
        # Use safe invocation with retries
        result: ExtractedClauses = safe_structured_invoke(structured_llm, prompt)
        return [clause.strip() for clause in result.clauses if clause.strip()]
    except Exception as exc:
        print(f"Error during clause extraction: {exc}")
        return []


# ============================================================
# STEP 2: Run each clause through Agentic RAG (Looping)
# ============================================================


def run_rag_check(clause: str, full_document: str) -> Dict[str, Any]:
    """Invoke the agentic RAG graph exported from looping.py."""
    question = f"""
You are checking one claim from a job offer against UK Skilled Worker
or Graduate visa requirements.

FULL JOB OFFER DOCUMENT:
{full_document}

CLAIM:
{clause}

Evaluate this claim using the full document and the retrieved
immigration rules.

You MUST:
1. Identify the specific immigration requirement that applies.
2. Identify which option, threshold, rule, exception, or condition
   applies to this particular case.
3. Identify the relevant value from the job offer.
4. Compare the job offer against the applicable requirement.
5. Determine whether the claim is:
   COMPLIANT
   NON_COMPLIANT
   or UNCLEAR.

Do not assume the general rule applies if a more specific option or
exception applies.

Use the full document to resolve missing context.
Do not invent facts.
If there is insufficient evidence, use UNCLEAR.

Explain the reasoning and identify the relevant rule.
"""

    # Hand off query execution directly to looping.py's graph
    result = rag_app.invoke(
        {
            "original_question": question,
            "current_query": question,
            "documents": [],
            "attempts": 0,
            "sufficient": False,
            "answer": "",
        }
    )

    return {
        "answer": result.get("answer", ""),
        "attempts": result.get("attempts", 0),
    }


# ============================================================
# STEP 3: Convert RAG analysis to structured JSON
# ============================================================


def structure_result(
    clause: str, rag_answer: str, attempts: int
) -> Dict[str, Any]:
    """Structure the RAG output using Pydantic enforcement."""
    structured_llm = llm.with_structured_output(ClauseAnalysis)

    prompt = f"""
Convert the following immigration analysis into structured output.

CLAUSE:
{clause}

RAG ANALYSIS:
{rag_answer}

First determine WHICH specific immigration requirement, option,
threshold, exception, or rule applies.

Then compare the document's facts against that requirement.

The status MUST be exactly one of:
COMPLIANT
NON_COMPLIANT
UNCLEAR

Use UNCLEAR when the available evidence is insufficient.
Do not invent information.
"""

    try:
        # Use safe invocation with retries
        analysis: ClauseAnalysis = safe_structured_invoke(structured_llm, prompt)

        return {
            "clause": clause,
            "status": analysis.status,
            "applicable_requirement": analysis.applicable_requirement,
            "document_value": analysis.document_value,
            "required_value": analysis.required_value,
            "reason": analysis.reason,
            "rule": analysis.rule,
            "attempts": attempts + 1,
        }

    except Exception as exc:
        return {
            "clause": clause,
            "status": "UNCLEAR",
            "applicable_requirement": "",
            "document_value": "",
            "required_value": "",
            "reason": f"Structuring failed: {str(exc)}",
            "rule": "",
            "attempts": attempts + 1,
        }


# ============================================================
# STEP 4: Check one clause
# ============================================================


def check_clause(clause: str, full_document: str) -> Dict[str, Any]:
    """Execute end-to-end check for a single clause."""
    rag_result = run_rag_check(clause=clause, full_document=full_document)

    return structure_result(
        clause=clause,
        rag_answer=rag_result["answer"],
        attempts=rag_result["attempts"],
    )


# ============================================================
# STEP 5: Full document pipeline (Throttled Concurrency)
# ============================================================


def check_document(
    document_text: str, max_workers: int = 1
) -> List[Dict[str, Any]]:
    """Extract clauses and run RAG checks sequentially with a delay to stay within Groq TPM limits."""
    clauses = extract_clauses(document_text)

    if not clauses:
        return []

    results: List[Dict[str, Any]] = [None] * len(clauses)  # type: ignore

    # Set max_workers=1 by default for free Groq accounts
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_index = {}
        for i, clause in enumerate(clauses):
            future = executor.submit(check_clause, clause, document_text)
            future_to_index[future] = (i, clause)
            # 2.0-second pause between submitting clause jobs to prevent TPM spikes
            time.sleep(2.0)

        for future in as_completed(future_to_index):
            i, clause = future_to_index[future]
            try:
                results[i] = future.result()
            except Exception as exc:
                results[i] = {
                    "clause": clause,
                    "status": "UNCLEAR",
                    "applicable_requirement": "",
                    "document_value": "",
                    "required_value": "",
                    "reason": f"Execution error in thread: {str(exc)}",
                    "rule": "",
                    "attempts": 1,
                }

    return results


# ============================================================
# STEP 6: Execute Directly
# ============================================================


if __name__ == "__main__":

    sample_document = """
    Job Offer Letter

    Dear Applicant,

    We are pleased to offer you the position of Software Engineer
    at TechCorp Ltd.

    Your annual salary will be £38,000, paid monthly.

    You will be sponsored under SOC code 2136
    (Programmers and software development professionals).

    Your contracted working hours will be 40 hours per week.

    This role does not require a criminal record certificate.

    TechCorp Ltd is an A-rated licensed sponsor.

    We look forward to welcoming you to the team.
    """

    # max_workers=1 ensures requests execute cleanly without hitting 6,000 TPM
    results = check_document(sample_document, max_workers=1)

    print(json.dumps(results, indent=4, ensure_ascii=False))