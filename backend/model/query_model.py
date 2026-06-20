from langchain_google_genai import ChatGoogleGenerativeAI
import os
def get_gemini_model():
    return ChatGoogleGenerativeAI(model="gemma-4-26b-a4b-it", google_api_key=os.getenv("GOOGLE_API_KEY"))
    # return ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))

