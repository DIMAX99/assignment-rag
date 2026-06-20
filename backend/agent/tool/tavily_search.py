# agent/tools/tavily_search.py
import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv() 

def get_tavily_client():
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("Environment variable 'TAVILY_API_KEY' is not set")
    return TavilyClient(api_key=api_key)

def search_biology_web(query: str) -> str:
    results = get_tavily_client().search(
        query=query,
        search_depth="basic",
        max_results=3,
        include_domains=["britannica.com", "khanacademy.org", "ncbi.nlm.nih.gov", "biology-online.org"]
    )

    if not results or not results.get("results"):
        return "No web results found."

    parts = []
    for i, r in enumerate(results["results"], start=1):
        parts.append(f"""
Web Source {i}
Title: {r['title']}
URL: {r['url']}

Content:
{r['content']}
""")

    return "\n\n".join(parts)
