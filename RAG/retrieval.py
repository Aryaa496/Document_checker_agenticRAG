#Load API key from .env
from dotenv import load_dotenv
load_dotenv()

#Import dependencies
#from chunking import chunks
from pinecone.grpc import PineconeGRPC as Pinecone
from test_questions import test_questions
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from pinecone import ServerlessSpec
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import ChatPromptTemplate
import time
import csv
import os

#Pinecone API key
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index_name = "compliance-checker"
index = pc.Index(index_name)
# HuggingFace model used for embeddings
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")

vectorstore = PineconeVectorStore(
    embedding=embeddings,
    index=index
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# 4. Set up the LLM (Groq, free tier)
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

# 5. Build the RAG chain
system_prompt = (
    "Use the given context to answer the question in the format of answering the question"
    "If the context doesn't contain the answer, say you don't know — do not guess. "
    "Keep the answer concise.\n\n{context}"
)
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
])

question_answer_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

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

    # crude automatic flag: did the model say some form of "I don't know"?
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
    })

    time.sleep(0.5)  # small delay to be polite to the free Groq tier's rate limits

# --- Save to CSV ---
output_path = "evaluation_results.csv"
with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["question", "category", "expected_answer", "model_answer", "said_dont_know", "sources"])
    writer.writeheader()
    writer.writerows(results)

print(f"\nSaved {len(results)} results to {output_path}")

# --- Quick summary stats ---
print("\n--- Quick summary ---")
for category in ["answerable", "synthesis", "unanswerable_trick"]:
    cat_results = [r for r in results if r["category"] == category]
    dont_know_count = sum(1 for r in cat_results if r["said_dont_know"])
    print(f"{category}: {len(cat_results)} questions, {dont_know_count} answered 'I don't know'")

print(
    "\nNote: for 'answerable' and 'synthesis' categories, a high 'I don't know' count is BAD "
    "(the system is failing to find real answers).\n"
    "For 'unanswerable_trick', a high 'I don't know' count is mostly GOOD, "
    "except for the 3 questions flagged NOTE in test_questions.py, which ARE answerable "
    "and should NOT say 'I don't know'.\n"
    "This summary is a rough automatic signal only — open evaluation_results.csv "
    "and manually check model_answer against expected_answer for real accuracy scoring."
)