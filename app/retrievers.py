from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from rank_bm25 import BM25Okapi
from app.utils import fetch_and_parse, split_text_into_documents
from app.config import EMBEDDING_MODEL_NAME

class BM25Retriever:
    def __init__(self, documents):
        self.documents = documents
        self.corpus = [doc.page_content for doc in documents]
        self.tokenized_corpus = [doc.page_content.split() for doc in documents]
        self.bm25 = BM25Okapi(self.tokenized_corpus)

    def retrieve(self, query, k=5):
        tokens = query.split()
        return self.bm25.get_top_n(tokens, self.corpus, n=k)

def load_documents_and_retrievers(topic: str):
    raw_text = fetch_and_parse(topic)

    if not raw_text or raw_text.startswith("No Wikipedia"):
        raise RuntimeError(f"Failed to fetch or parse topic: {topic}")

    docs = split_text_into_documents(raw_text)

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    chroma_store = Chroma(embedding_function=embeddings)
    chroma_store.add_documents(docs)
    bm25 = BM25Retriever(docs)
    return docs, chroma_store, bm25

