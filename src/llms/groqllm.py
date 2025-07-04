from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

class GroqLLM:
    def __init__(self):
        load_dotenv()

    def get_llm(self):
        try:
            os.environ["GROQ_API_KEY"] = self.groq_api_key = os.getenv("GROQ_API_KEY")
            llm = ChatGroq(api_key=self.groq_api_key, model="llama3-8b-8192")

            return llm
        except Exception as e:
            raise ValueError(f"Error occurred with exception : {e}")
