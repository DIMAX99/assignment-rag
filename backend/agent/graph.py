import base64

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage

from agent.state import AgentState
from model.query_model import get_gemini_model
from agent.utils.image_loader import download_image_from_url
from db.db import get_vector_store
from model.embedding_model import get_google_embedding
from agent.utils.extract_text import extract_text

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

    image_summary = extract_text(response.content)

    return {
        "image_summary": image_summary
    }

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
{state.image_summary if state.image_summary else "No image was provided."}

Return only the search query.
"""

    message = HumanMessage(content=prompt)
    response = await model.ainvoke([message])
    search_query = extract_text(response.content)

    return {
        "search_query": search_query
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
You are a helpful study assistant for a textbook-based RAG chatbot.

Your task is to answer the student's question using only:
1. The retrieved textbook context
2. The image summary, if an image was provided

You must not use outside knowledge unless it is directly supported by the retrieved context or image summary.

Student question:
{state.question}

Image summary:
{state.image_summary if state.image_summary else "No image was provided."}

Retrieved textbook context:
{state.retrieved_context}

Answering rules:
- Give a clear, student-friendly explanation.
- Use the retrieved textbook context as the main source of truth.
- If the image summary is relevant, connect it to the textbook context.
- If the image summary is not relevant, ignore it.
- Do not invent facts, definitions, examples, page numbers, or source names.
- If the retrieved context does not contain enough information to answer the question, respond exactly with:
Information not found.
- Keep the answer concise but complete.
- Use simple language unless the textbook context requires technical terms.
- Do not mention that you are an AI model.
- Do not say "based on the context" repeatedly.

Final answer:
"""
    message = HumanMessage(content=prompt)
    response = await model.ainvoke([message])

    
    final_text = extract_text(response.content)

    return {
        "final_answer": final_text
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