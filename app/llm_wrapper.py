from langchain.chat_models import ChatOpenAI
from app.config import GROQ_MODEL
from dotenv import load_dotenv
import os

def setup_llm():
    load_dotenv()  

    return ChatOpenAI(
        model=GROQ_MODEL,
        temperature=0.7,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_api_base=os.getenv("OPENAI_API_BASE"),
    )
