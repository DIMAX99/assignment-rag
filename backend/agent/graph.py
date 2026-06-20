import base64

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage

from agent.state import AgentState
from model.query_model import get_gemini_model
from agent.utils.image_loader import download_image_from_url
from db.db import get_vector_store
from model.embedding_model import get_google_embedding
from agent.utils.extract_text import extract_text
from agent.tool.tavily_search import search_biology_web

BIOLOGY_KEYWORDS = [
    "cell", "biology", "organism", "DNA", "RNA", "protein", "gene", "evolution",
    "ecosystem", "photosynthesis", "mitosis", "meiosis", "enzyme", "species",
    "habitat", "reproduction", "nervous system", "metabolism", "bacteria", "virus"
]

WEB_SEARCH_KEYWORDS = [
    "search", "look up", "find online", "web", "internet", "latest", "recent", "current"
]

def is_biology_query(question: str) -> bool:
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in BIOLOGY_KEYWORDS)

def wants_web_search(question: str) -> bool:
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in WEB_SEARCH_KEYWORDS)

# CHANGE 1 - updated routing logic
def should_use_web_fallback(state: AgentState) -> str:
    no_context = (
        not state.retrieved_context or
        state.retrieved_context == "No relevant textbook context found."
    )

    is_biology = is_biology_query(state.question)
    wants_search = wants_web_search(state.question)

    if no_context and is_biology:
        return "web_fallback"

    if wants_search and is_biology:
        return "web_fallback"

    return "answer"

# CHANGE 2 - combine textbook + web when both exist
async def web_fallback_node(state: AgentState):
    query = state.search_query or state.question
    web_context = search_biology_web(query)

    no_context = (
        not state.retrieved_context or
        state.retrieved_context == "No relevant textbook context found."
    )

    if not no_context:
        combined_context = f"""
Textbook Context:
{state.retrieved_context}

Web Search Results:
{web_context}
"""
    else:
        combined_context = f"""
Web Search Results:
{web_context}
"""

    return {
        "retrieved_context": combined_context,
        "used_web_fallback": True
    }

async def analyze_image_node(state: AgentState):
    if not state.image_url:
        return {"image_summary": None}

    downloaded = await download_image_from_url(state.image_url)
    image_bytes = downloaded["image_bytes"]
    mime_type = downloaded["content_type"]
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    model = get_gemini_model()

    prompt = f"""
Analyze this image based on the user's question.

User question:
{state.question}

Give a useful summary of the image.
If the image contains text, labels, diagrams, charts, tables, textbook content, or objects, mention the important details.
"""

    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_base64}"}},
        ]
    )

    response = await model.ainvoke([message])
    return {"image_summary": extract_text(response.content)}

async def build_query_node(state: AgentState):
    if not state.image_summary:
        return {"search_query": state.question}

    model = get_gemini_model()

    prompt = f"""
You are creating a retrieval query for a textbook RAG system.

Your job is to convert the user's question and the image summary into a clear, concise, search-friendly query that will retrieve the most relevant textbook chunks from a vector database.

Focus on:
- the main concept being asked about
- important scientific/technical terms
- labels, objects, diagrams, processes, or relationships mentioned in the image
- the user's actual intent

Avoid:
- unnecessary explanation
- conversational wording
- phrases like "the user wants to know"
- adding facts that are not present in the question or image summary

User question:
{state.question}

Image summary:
{state.image_summary}

Return only the search query.
"""

    message = HumanMessage(content=prompt)
    response = await model.ainvoke([message])
    return {"search_query": extract_text(response.content)}

async def retrieve_node(state: AgentState):
    vector_store = get_vector_store()
    query = state.search_query or state.question

    docs = vector_store.similarity_search(query=query, k=5)

    if not docs:
        return {"retrieved_context": "No relevant textbook context found."}

    context_parts = []
    for i, doc in enumerate(docs, start=1):
        metadata = doc.metadata or {}
        source = metadata.get("source", "Unknown source")
        page = metadata.get("page", "Unknown page")
        context_parts.append(f"""
Source {i}
File: {source}
Page: {page}

Content:
{doc.page_content}
""")

    return {"retrieved_context": "\n\n".join(context_parts)}

# CHANGE 3 - updated answer prompt to handle combined sources
async def answer_node(state: AgentState):
    model = get_gemini_model()

    prompt = f"""
You are a helpful study assistant for a textbook-based RAG chatbot.

Your task is to answer the student's question using:
1. The retrieved textbook context (if available) — treat this as the primary source
2. Web search results (if available) — use as a supplement when textbook context is missing or incomplete
3. The image summary (if an image was provided)

Student question:
{state.question}

Image summary:
{state.image_summary if state.image_summary else "No image was provided."}

Retrieved context:
{state.retrieved_context}

Answering rules:
- Prioritize textbook context over web results when both are available.
- Give a clear, student-friendly explanation.
- If the image summary is relevant, connect it to the context.
- If the image summary is not relevant, ignore it.
- Do not invent facts, definitions, examples, page numbers, or source names.
- If neither the context nor web results contain enough information, respond exactly with:
Information not found.
- Keep the answer concise but complete.
- Use simple language unless the context requires technical terms.
- Do not mention that you are an AI model.
- Do not say "based on the context" repeatedly.

Final answer:
"""

    message = HumanMessage(content=prompt)
    response = await model.ainvoke([message])
    return {"final_answer": extract_text(response.content)}

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("analyze_image", analyze_image_node)
    graph.add_node("build_query", build_query_node)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("web_fallback", web_fallback_node)
    graph.add_node("answer", answer_node)

    graph.set_entry_point("analyze_image")

    graph.add_edge("analyze_image", "build_query")
    graph.add_edge("build_query", "retrieve")

    graph.add_conditional_edges(
        "retrieve",
        should_use_web_fallback,
        {
            "web_fallback": "web_fallback",
            "answer": "answer"
        }
    )

    graph.add_edge("web_fallback", "answer")
    graph.add_edge("answer", END)

    return graph.compile()

app_graph = build_graph()