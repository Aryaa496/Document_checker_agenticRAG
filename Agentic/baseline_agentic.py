# agentic_evaluate.py
#
# Runs all 71 test questions through the AGENTIC RAG system (looping.py) —
# the self-correcting retrieve -> judge -> rewrite -> answer loop — and
# saves results to a CSV. This is the "after" measurement to compare
# against the baseline.
#
# Place this in Agentic/, alongside looping.py, test_questions.py
# (copy test_questions.py into this folder too, or adjust the import path)

from dotenv import load_dotenv
load_dotenv()

import csv
import time
from looping import app as rag_app

from test_questions import test_questions

results = []

for i, item in enumerate(test_questions):
    print(f"[{i+1}/{len(test_questions)}] {item['question'][:70]}...")

    try:
        result = rag_app.invoke({
            "original_question": item["question"],
            "current_query": item["question"],
            "documents": [],
            "attempts": 0,
            "sufficient": False,
            "answer": "",
        })
        answer = result["answer"]
        attempts_taken = result["attempts"] + 1
    except Exception as e:
        answer = f"ERROR: {e}"
        attempts_taken = 0

    said_dont_know = any(
        phrase in answer.lower()
        for phrase in ["i don't know", "i do not know", "not stated", "cannot find",
                       "no information", "not applicable", "don't have enough information"]
    )

    results.append({
        "question": item["question"],
        "category": item["category"],
        "expected_answer": item["expected_answer"],
        "model_answer": answer,
        "said_dont_know": said_dont_know,
        "attempts_taken": attempts_taken,
        "system": "agentic",
    })

    time.sleep(0.5)

output_path = "agentic_results.csv"
with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "question", "category", "expected_answer", "model_answer",
        "said_dont_know", "attempts_taken", "system"
    ])
    writer.writeheader()
    writer.writerows(results)

print(f"\nSaved {len(results)} agentic results to {output_path}")

print("\n--- Quick summary ---")
for category in ["answerable", "synthesis", "unanswerable_trick"]:
    cat_results = [r for r in results if r["category"] == category]
    dont_know_count = sum(1 for r in cat_results if r["said_dont_know"])
    avg_attempts = sum(r["attempts_taken"] for r in cat_results) / len(cat_results) if cat_results else 0
    print(f"{category}: {len(cat_results)} questions, {dont_know_count} answered 'I don't know', avg {avg_attempts:.1f} attempts")