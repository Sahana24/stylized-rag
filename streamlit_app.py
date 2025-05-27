import streamlit as st
from app.rag_pipeline import build_rag_chain
from app.retrievers import load_documents_and_retrievers
from app.llm_wrapper import setup_llm
from app.config import DEFAULT_STYLE, DEFAULT_QUERY
import logging

st.set_page_config(page_title="Stylized RAG", layout="wide")
st.title("📝 Stylized Retrieval-Augmented Generation")
st.markdown(
    "This app retrieves context from a Wikipedia article and rewrites your input in a selected style. "
    "To begin, enter a topic in the sidebar and load it before using the style rewriter below."
)

logging.basicConfig(level=logging.INFO)

st.sidebar.header("Settings")

topic = st.sidebar.text_input("Wikipedia Topic", value="Artificial Intelligence")
style = st.sidebar.text_input("Target Writing Style", value=DEFAULT_STYLE)

if st.sidebar.button("Load Wikipedia Content"):
    with st.spinner("Fetching and indexing Wikipedia content..."):
        try:
            documents, chroma_store, bm25_retriever = load_documents_and_retrievers(topic)

            if not documents:
                st.warning(f"No Wikipedia content found for: **{topic}**. Try a different topic.")
                st.stop()

            llm = setup_llm()
            rag_chain = build_rag_chain(llm, chroma_store, bm25_retriever)
            st.session_state["rag_chain"] = rag_chain
            st.success(f"✅ Content loaded for topic: {topic}")

        except Exception as e:
            st.error("Something went wrong while loading the Wikipedia content.")
            logging.exception("Wikipedia topic loading failed:")
            st.stop()


# Main input box
original_text = st.text_area("Enter your text:", value=DEFAULT_QUERY, height=150)

if st.button("Rewrite in Style"):
    if not original_text.strip():
        st.warning("Please enter some input text.")
    elif "rag_chain" not in st.session_state:
        st.warning("Please load a Wikipedia topic first from the sidebar.")
    else:
        inputs = {
            "question": original_text,
            "style": style,
            "original_text": original_text
        }
        try:
            with st.spinner("Generating styled output..."):
                output = st.session_state["rag_chain"](inputs)
            st.subheader("✍️ Styled Output")
            st.write(output)
        except Exception as e:
            logging.exception("Error during generation:")
            st.error("An error occurred while generating the output. Please try again.")