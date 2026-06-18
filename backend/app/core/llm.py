import os
from langchain_google_genai import ChatGoogleGenerativeAI

def get_llm():
    """
    Returns the LLM instance to be used across agents.
    Using Gemini as the default model.
    Make sure GOOGLE_API_KEY is set in your environment variables.
    """
    # Assuming the API key is set in the environment or user configuration
    return ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0)
