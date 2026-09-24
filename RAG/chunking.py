
from langchain_community.document_loaders import DirectoryLoader, TextLoader 
#Used DirectoryLoader and TextLoader to Load and extract the document

#Load the splitter to break the document into chunks
from langchain_text_splitters import RecursiveCharacterTextSplitter 

# Loading the directory as a whole since we have two textual documents on the skiled worker visa and graduate visa rules.
loader=DirectoryLoader("data/rulebook",
                       glob="*.txt",
                       loader_cls=TextLoader) 

documents=loader.load()
# A check to establish that the documents have been loaded effectively
print(f"Loaded {len(documents)} documents")

#Splitting the document into chunks
splitter=RecursiveCharacterTextSplitter(chunk_size=500, #500 characters per chunk
                                        chunk_overlap=50, #50 characters overlap so that characters arent lost
                                        separators=["\n\n", "\n", ". ", " ", ""] #splits on paragraph breaks
                                        )
chunks = splitter.split_documents(documents)
print(f"Created {len(chunks)} chunks total\n")

#Print each chunk so you can actually see where it cut
for i, chunk in enumerate(chunks):
    print(f"--- Chunk {i} (source: {chunk.metadata['source']}) ---")
    print(chunk.page_content)
    print(f"[{len(chunk.page_content)} characters]\n")