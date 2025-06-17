from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore



load_dotenv()


urls = [
    "https://bikehero.sg/bike-servicing-and-repair-pricing",
    "https://bikehero.sg/faq",
    # Add more subpages here if needed
]


docs = [WebBaseLoader(url).load() for url in urls]
docs_list = [item for sublist in docs for item in sublist]


# Optional: split text for better chunking
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=250, chunk_overlap=0
)
doc_splits = text_splitter.split_documents(docs_list)

embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# PineconeVectorStore.from_documents(
#     documents=doc_splits, 
#     embedding=embedding, 
#     index_name="superbench")


# vectorstore = Chroma.from_documents(
#     documents=doc_splits,
#     collection_name="rag-chroma",
#     embedding=GoogleGenerativeAIEmbeddings(model="models/embedding-001"),
#     persist_directory="./.chroma",
# )


# retriever = Chroma(
#     collection_name="rag-chroma",
#     persist_directory="./.chroma",
#     embedding_function=GoogleGenerativeAIEmbeddings(model="models/embedding-001"),
# ).as_retriever()

retriever = PineconeVectorStore(index_name="superbench", embedding=embedding).as_retriever()


