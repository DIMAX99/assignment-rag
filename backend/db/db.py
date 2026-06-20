import os
import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

# Add backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_postgres import PGVector
from model.embedding_model import get_google_embedding, get_embedding_model_hf

def get_db_connection_string():
    """
    Retrieves the database connection string from environment variables.
    """
    db_connection_string = os.getenv('SUPABASE_DATABASE_URL')
    if not db_connection_string:
        raise ValueError("Environment variable 'SUPABASE_DATABASE_URL' is not set")
    return db_connection_string

db_connection_string = get_db_connection_string()
# embeddings=get_google_embedding()
embeddings=get_google_embedding()


def get_vector_store():
    """
    Initializes and returns a PGVector instance for vector storage.
    
    Returns:
        PGVector: An instance of PGVector configured with the specified embeddings and database connection string.
    """
    vectorStore=PGVector(
        embeddings=embeddings,
        connection=db_connection_string,
        collection_name="documents",
        use_jsonb=True
    )
    return vectorStore