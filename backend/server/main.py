from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional
from uuid import uuid4
from agent.graph import app_graph

app = FastAPI(title="Multimodal RAG Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later replace with your Vercel frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    image_url: Optional[str] = None
    image_path: Optional[str] = None


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Backend server is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/chat")
async def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )

    # session_id = req.session_id or str(uuid4())

    result = await app_graph.ainvoke({
        "question": req.message,
        "image_url": req.image_url
    })
    return {
    "answer": result["final_answer"],
    "used_web_fallback": result.get("used_web_fallback", False)
    }