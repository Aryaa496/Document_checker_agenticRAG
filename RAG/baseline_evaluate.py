# baseline_evaluate.py
#
# Runs all 71 test questions through the BASELINE (non-agentic) RAG chain —
# single retrieve-then-answer pass, no self-correction loop — and saves
# results to a CSV. This is the "before" measurement to compare against
# the agentic version.
#
# Place this in RAG/, alongside retrieval.py, chunking.py, test_questions.py

from dotenv import load_dotenv
load_dotenv()

import csv
import time
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
import os

from test_questions import test_questions

# --- Set up the baseline RAG chain (same as retrieval.py) ---
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index_name = "compliance-checker"
index = pc.Index(index_name)

embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
vectorstore = PineconeVectorStore(index=index, embedding=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

system_prompt = (
    "Use the given context to answer the question. "
    "If the context doesn't contain the answer, say you don't know — do not guess. "
    "Keep the answer concise.\n\n{context}"
)
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
])

question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

# --- Run every question through the baseline chain and log results ---
results = []

for i, item in enumerate(test_questions):
    print(f"[{i+1}/{len(test_questions)}] {item['question'][:70]}...")

    try:
        response = rag_chain.invoke({"input": item["question"]})
        answer = response["answer"]
        sources = [doc.metadata.get("source", "unknown") for doc in response["context"]]
    except Exception as e:
        answer = f"ERROR: {e}"
        sources = []

    said_dont_know = any(
        phrase in answer.lower()
        for phrase in ["i don't know", "i do not know", "not stated", "cannot find", "no information", "not applicable"]
    )

    results.append({
        "question": item["question"],
        "category": item["category"],
        "expected_answer": item["expected_answer"],
        "model_answer": answer,
        "said_dont_know": said_dont_know,
        "sources": "; ".join(sources),
        "system": "baseline",
    })

    time.sleep(0.5)

output_path = "baseline_results.csv"
with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "question", "category", "expected_answer", "model_answer",
        "said_dont_know", "sources", "system"
    ])
    writer.writeheader()
    writer.writerows(results)

print(f"\nSaved {len(results)} baseline results to {output_path}")

print("\n--- Quick summary ---")
for category in ["answerable", "synthesis", "unanswerable_trick"]:
    cat_results = [r for r in results if r["category"] == category]
    dont_know_count = sum(1 for r in cat_results if r["said_dont_know"])
    print(f"{category}: {len(cat_results)} questions, {dont_know_count} answered 'I don't know'")