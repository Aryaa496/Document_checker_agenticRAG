from pinecone.grpc import PineconeGRPC as Pinecone
import os
from dotenv import load_dotenv
load_dotenv()

pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])

for idx in pc.list_indexes():
    stats = pc.Index(idx.name).describe_index_stats()
    print(f"Index: '{idx.name}' -> vector count: {stats['total_vector_count']}")