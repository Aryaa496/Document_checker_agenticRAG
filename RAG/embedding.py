from dotenv import load_dotenv
load_dotenv()

from chunking import chunks
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
import os

#Pinecone API key
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])

index_name = "compliance-checker"

if index_name not in [i.name for i in pc.list_indexes()]:
    pc.create_index(
        name=index_name,
        dimension=384,   # bge-small-en-v1.5 outputs 384-dimensional vectors
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

# Free, local embedding model — runs on your machine, no API key or cost
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")

vectorstore = PineconeVectorStore.from_documents(
    documents=chunks,
    embedding=embeddings,
    index_name=index_name
)

print(f"Stored {len(chunks)} chunks in Pinecone index '{index_name}'")

query = "What is the salary threshold for a Skilled Worker visa?"
results = vectorstore.similarity_search(query, k=3)

for i, doc in enumerate(results):
    print(f"\n--- Result {i+1} (source: {doc.metadata['source']}) ---")
    print(doc.page_content)