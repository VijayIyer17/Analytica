import os
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings

def get_llm():
    """
    Returns the LLM instance to be used across agents.
    Using Gemini as the default model.
    """
    if not settings.GOOGLE_API_KEY or settings.GOOGLE_API_KEY == "your_google_api_key_here":
        raise ValueError("GOOGLE_API_KEY is not configured. Please set it in backend/.env")
        
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-pro", 
        temperature=0,
        google_api_key=settings.GOOGLE_API_KEY
    )
