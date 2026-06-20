from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
def get_google_embedding():
    return GoogleGenerativeAIEmbeddings(model="gemini-embedding-001", google_api_key=os.getenv("GOOGLE_API_KEY"))
# from langchain_huggingface import HuggingFaceEmbeddings

# def get_embedding_model_hf():
#     return HuggingFaceEmbeddings(
#         model_name="BAAI/bge-small-en-v1.5",
#         model_kwargs={"device": "cpu"},
#         encode_kwargs={"normalize_embeddings": True},
#     )

