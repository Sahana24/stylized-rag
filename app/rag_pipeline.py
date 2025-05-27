from app.utils import format_docs
from langchain.prompts import PromptTemplate
from langchain.schema import Document
import logging

class EnsembleRetriever:
    def __init__(self, chroma_store, bm25_retriever):
        self.chroma_store = chroma_store
        self.bm25_retriever = bm25_retriever

    def get_relevant_documents(self, query: str, k: int = 5):
        try:
            chroma_docs = self.chroma_store.similarity_search(query, k=k)
        except Exception as e:
            logging.warning(f"Chroma retrieval failed: {e}")
            chroma_docs = []

        try:
            bm25_docs = self.bm25_retriever.retrieve(query, k=k)
        except Exception as e:
            logging.warning(f"BM25 retrieval failed: {e}")
            bm25_docs = []

        combined = chroma_docs + [Document(page_content=doc) if isinstance(doc, str) else doc for doc in bm25_docs]
        seen = set()
        unique_docs = []
        for doc in combined:
            key = doc.page_content[:60]
            if key not in seen:
                unique_docs.append(doc)
                seen.add(key)
        return unique_docs[:k]

style_prompt = PromptTemplate(
    input_variables=["style", "context", "original_text"],
    template=(
        "Rewrite the following text in a {style} style:\n\n"
        "Context:\n{context}\n\n"
        "Original:\n{original_text}\n\n"
        "Styled:"
    )
)
class StrOutputParser:
    def parse(self, message):
        return message.content.strip()

def build_rag_chain(llm, chroma_store, bm25_retriever):
    ensemble = EnsembleRetriever(chroma_store, bm25_retriever)

    def rag_chain(inputs):
        try:
            query = inputs["question"]
            context = format_docs(ensemble.get_relevant_documents(query))
            prompt = style_prompt.format(
                style=inputs["style"],
                context=context,
                original_text=inputs["original_text"]
            )
            logging.info("Sending prompt to model...")
            response = llm.invoke(prompt)
            logging.info("Received response from LLM.")
            return StrOutputParser().parse(response)
        except Exception as e:
            logging.exception("RAG chain failed:")
            return "Sorry, something went wrong while generating the styled output."

    return rag_chain
