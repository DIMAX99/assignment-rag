import base64

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage

from agent.state import AgentState
from model.query_model import get_gemini_model
from server.service.image_loader import download_image_from_url
from db.db import get_vector_store
from model.embedding_model import get_google_embedding

async def analyze_image_node(state: AgentState):
    if not state.image_url:
        return {
            "image_summary": None
        }

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
            {
                "type": "text",
                "text": prompt,
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{image_base64}"
                },
            },
        ]
    )

    response = await model.ainvoke([message])

    return {
        "image_summary": response.content
    }

async def build_query_node(state: AgentState):
    if not state.image_summary:
        return {"search_query": state.question}

    model = get_gemini_model()

    prompt = f"""
Given a user's question and an image summary, generate a concise search query (1-2 sentences max) to retrieve relevant textbook content.

User question: {state.question}
Image summary: {state.image_summary}

Return only the search query, nothing else.
"""

    message = HumanMessage(content=prompt)
    response = await model.ainvoke([message])

    return {
        "search_query": response.content.strip()
    }
async def retrieve_node(state: AgentState):
    vector_store = get_vector_store()
    query = state.search_query or state.question

    docs = vector_store.similarity_search(
        query=query,
        k=5
    )

    if not docs:
        return {
            "retrieved_context": "No relevant textbook context found."
        }

    context_parts = []

    for i, doc in enumerate(docs, start=1):
        metadata = doc.metadata or {}

        source = metadata.get("source", "Unknown source")
        page = metadata.get("page", "Unknown page")

        context_parts.append(
            f"""
Source {i}
File: {source}
Page: {page}

Content:
{doc.page_content}
"""
        )

    retrieved_context = "\n\n".join(context_parts)

    return {
        "retrieved_context": retrieved_context
    }

async def answer_node(state: AgentState):
    model = get_gemini_model()

    prompt = f"""
You are a helpful study assistant. Answer the student's question using the retrieved textbook context.

Question:
{state.question}

{"Image Summary:" + state.image_summary if state.image_summary else ""}

Retrieved Context:
{state.retrieved_context}

Instructions:
- Answer clearly and concisely based on the context provided.
- If the context doesn't contain enough information, say "Information not found."
- Do not make up information.
"""

    message = HumanMessage(content=prompt)
    response = await model.ainvoke([message])

    return {
        "final_answer": response.content
    }
def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("analyze_image", analyze_image_node)
    graph.add_node("build_query", build_query_node)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("answer", answer_node)

    graph.set_entry_point("analyze_image")

    graph.add_edge("analyze_image", "build_query")
    graph.add_edge("build_query", "retrieve")
    graph.add_edge("retrieve", "answer")
    graph.add_edge("answer", END)

    return graph.compile()


app_graph = build_graph()