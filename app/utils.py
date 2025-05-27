from langchain.schema import Document
import wikipedia

def fetch_and_parse(topic: str) -> str:
    try:
        wikipedia.set_lang("en")
        summary = wikipedia.page(topic).content
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Looks like your search was too broad. Try a more specific topic. Options include: {e.options[:5]}"
    except wikipedia.exceptions.PageError:
        return f"No Wikipedia article found for: {topic}"
    except Exception as e:
        return f"Error fetching Wikipedia content: {e}"

def split_text_into_documents(text: str, chunk_size=1000, overlap=100):
    docs = []
    start = 0
    while start < len(text):
        chunk = text[start:start + chunk_size]
        if chunk.strip():
            docs.append(Document(page_content=chunk))
        start += chunk_size - overlap
    return docs

def format_docs(docs):
    if not docs:
        return "No relevant context found."
    return "\n".join([f"{i+1}. {doc.page_content.strip()}" for i, doc in enumerate(docs)])