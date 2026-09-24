# This builds an "agentic RAG" system using LangGraph — instead of a single
# retrieve-then-answer pass (like the baseline in RAG/retrieval.py), this
# version checks whether what it retrieved is actually good enough, and if
# not, rewrites the search query and tries again (up to a limit) before
# giving an honest "I don't know" instead of guessing.

import os
from typing import List, TypedDict
from dotenv import load_dotenv

# Import tenacity for handling 429 Rate Limit retries
from tenacity import retry, stop_after_attempt, wait_exponential

# 1. REPLACE HuggingFaceEmbeddings WITH FastEmbed
from langchain_community.embeddings import FastEmbedEmbeddings

from langchain_core.documents import Document
from langchain_groq import ChatGroq
from langchain_pinecone import PineconeVectorStore
from langgraph.graph import END, StateGraph
from pinecone import Pinecone

load_dotenv()

pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index = pc.Index("compliance-checker")

# 2. USE BAAI/bge-small-en-v1.5 VIA FASTEMBED (THREAD-SAFE & PYTORCH-FREE)
embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")
vectorstore = PineconeVectorStore(index=index, embedding=embeddings)

retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)


# ============================================================
# RATE LIMIT SAFEGUARD (TENACITY RETRY LOGIC)
# ============================================================
@retry(
    wait=wait_exponential(min=3, max=30),  # Wait 3s, 6s, 12s... up to 30s
    stop=stop_after_attempt(5),            # Retry up to 5 times before failing
    reraise=True,
)
def safe_llm_invoke(prompt_or_messages):
    """Safely invoke LLM with backoff to bypass Groq 429 rate limit spikes."""
    return llm.invoke(prompt_or_messages)


# Define the state that flows through the graph
# Each node reads from it and writes updates back into it
class GraphState(TypedDict):
    original_question: str  # The original question asked is of string type
    current_query: str      # Search query being tested, could change upon new retries
    documents: List[Document]  # Whatever chunks are being retrieved
    attempts: int           # Will keep maximum attempts 3
    sufficient: bool
    answer: str


# Define the nodes of the graph

# search pinecone based on current query and then retrieve the documents/chunks
def retrieve(state: GraphState) -> GraphState:
    docs = retriever.invoke(state["current_query"])
    #for i, d in enumerate(docs):
        #print(f"  [{i}] {d.metadata.get('source')}: {d.page_content[:100]}")
    state["documents"] = docs
    return state


# Ask the LLM to judge its own retrieved content. Is it good enough to fully answer its original question.
def judge_sufficiency(state: GraphState) -> GraphState:
    context = "\n\n".join(doc.page_content for doc in state["documents"])

    judge_prompt = f""" Question :{state['original_question']}

Retrieved context
{context}

Does this context contain enough information to fully and correctly answer the question?
Reply with only one word: YES or NO."""

    # Using safe_llm_invoke instead of direct llm.invoke
    response = safe_llm_invoke(judge_prompt)
    state["sufficient"] = "YES" in response.content.upper()
    return state


# Rewrite the query if we get a "NO" and increment the count so that we don't loop more than 3 times.
def rewrite_query(state: GraphState) -> GraphState:
    rewrite_prompt = f"""The following search query did not retrieve enough information to answer the question.

This is specifically about the UK Immigration Rules — Skilled Worker and Graduate visa routes ONLY. Do not reference any other country's visa system (e.g. US H-1B, other national schemes).

Original question: {state['original_question']}
Query that was tried: {state['current_query']}

Write a single, different, more specific UK immigration search query that might retrieve better results. Reply with ONLY the new query, nothing else."""

    # Using safe_llm_invoke instead of direct llm.invoke
    response = safe_llm_invoke(rewrite_prompt)
    state["current_query"] = response.content.strip()
    state["attempts"] += 1
    return state


# If the answer was judged sufficiently answer normally but if 3 tries were made, answer with I don't know.
def generate_answer(state: GraphState) -> GraphState:
    if not state["sufficient"]:
        state["answer"] = (
            "I don't have enough information in the rulebook to answer this question confidently."
        )
        return state

    context = "\n\n".join(doc.page_content for doc in state["documents"])
    answer_prompt = f"""Use the given context to answer the question. If the context doesn't contain the answer, say you don't know — do not guess.

Context:
{context}

Question: {state['original_question']}

Answer:"""

    # Using safe_llm_invoke instead of direct llm.invoke
    response = safe_llm_invoke(answer_prompt)
    state["answer"] = response.content
    return state


# Defining the main routing logic conditional stage
def should_retry(state: GraphState) -> str:
    if state["sufficient"]:
        return "generate"
    if state["attempts"] >= 2:
        return "generate"
    return "rewrite"


# Building the main graph
graph = StateGraph(GraphState)

graph.add_node("retrieve", retrieve)
graph.add_node("judge", judge_sufficiency)
graph.add_node("rewrite", rewrite_query)
graph.add_node("generate", generate_answer)

graph.set_entry_point("retrieve")  # every run starts here
graph.add_edge("retrieve", "judge")  # always judge right after retrieving
graph.add_conditional_edges(
    "judge", should_retry, {"rewrite": "rewrite", "generate": "generate"}
)  # judge branches based on should_retry()
graph.add_edge("rewrite", "retrieve")  # after rewriting, loop back to retrieve
graph.add_edge("generate", END)  # generating an answer always ends the run

app = graph.compile()

if __name__ == "__main__":
    question = "What SOC occupation code does a Graduate route applicant need?"
    # this is the STARTING state — every field in GraphState needs an initial value
    result = app.invoke({
        "original_question": question,
        "current_query": question,  # starts the same as the original question
        "documents": [],
        "attempts": 0,
        "sufficient": False,
        "answer": "",
    })

    print("Final answer:", result["answer"])
    print("Attempts taken:", result["attempts"] + 1)