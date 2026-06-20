import os
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

# Ensure environment variables are loaded before initializing
if not url or not key:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables must be set.")

# This creates a single, reusable client instance
supabase: Client = create_client(url, key)