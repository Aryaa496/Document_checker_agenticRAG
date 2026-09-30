# compare_results.py
#
# Reads baseline_results.csv and agentic_results.csv and produces a
# side-by-side comparison. This is the actual "finding" for your project —
# run this AFTER both baseline_evaluate.py and agentic_evaluate.py have
# been run, and after you've manually reviewed/scored correctness.
#
# NOTE: "said_dont_know" is an automatic keyword-based signal, not true
# accuracy. For a real accuracy number, open both CSVs and manually mark
# whether model_answer actually matches expected_answer for the
# "answerable" and "synthesis" categories — the automatic flag only tells
# you abstention behavior, not correctness of the answers it DID give.
#
# Place this wherever convenient, and pass the paths to both CSVs.

import pandas as pd

BASELINE_CSV = "baseline_results.csv"   # copy this from RAG/ folder
AGENTIC_CSV = "agentic_results.csv"     # copy this from Agentic/ folder

baseline_df = pd.read_csv(BASELINE_CSV)
agentic_df = pd.read_csv(AGENTIC_CSV)

print("=" * 70)
print("BASELINE vs AGENTIC — 'I don't know' rate by category")
print("(this is an ABSTENTION signal, not accuracy — see note below)")
print("=" * 70)

for category in ["answerable", "synthesis", "unanswerable_trick"]:
    b = baseline_df[baseline_df["category"] == category]
    a = agentic_df[agentic_df["category"] == category]

    b_dk = b["said_dont_know"].sum()
    a_dk = a["said_dont_know"].sum()
    b_total = len(b)
    a_total = len(a)

    print(f"\n{category} ({b_total} questions)")
    print(f"  Baseline : {b_dk}/{b_total} said 'I don't know' ({100*b_dk/b_total:.0f}%)")
    print(f"  Agentic  : {a_dk}/{a_total} said 'I don't know' ({100*a_dk/a_total:.0f}%)")

    if category in ("answerable", "synthesis"):
        print(f"  -> LOWER is better here (these should be answerable)")
    else:
        print(f"  -> HIGHER is better here (should correctly decline, except the 3 NOTE-flagged trick questions)")

print("\n" + "=" * 70)
print("Average retrieval attempts (agentic only — baseline is always 1)")
print("=" * 70)
if "attempts_taken" in agentic_df.columns:
    for category in ["answerable", "synthesis", "unanswerable_trick"]:
        a = agentic_df[agentic_df["category"] == category]
        print(f"{category}: avg {a['attempts_taken'].mean():.2f} attempts")

# --- Merge into one file for manual accuracy review ---
merged = baseline_df[["question", "category", "expected_answer", "model_answer", "said_dont_know"]].rename(
    columns={"model_answer": "baseline_answer", "said_dont_know": "baseline_dont_know"}
)
agentic_slim = agentic_df[["question", "model_answer", "said_dont_know", "attempts_taken"]].rename(
    columns={"model_answer": "agentic_answer", "said_dont_know": "agentic_dont_know"}
)
merged = merged.merge(agentic_slim, on="question", how="left")

# empty columns for you to manually fill in True/False after reviewing each row
merged["baseline_correct"] = ""
merged["agentic_correct"] = ""

merged.to_csv("comparison_for_manual_review.csv", index=False)
print("\nSaved comparison_for_manual_review.csv")
print("Open this file, read each row, and fill in baseline_correct / agentic_correct")
print("(TRUE/FALSE) by comparing model_answer against expected_answer.")
print("Then re-run with those columns filled to get real accuracy numbers.")
