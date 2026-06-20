from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional
from uuid import uuid4
from server.service.image_loader import download_image_from_url

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

    session_id = req.session_id or str(uuid4())

    image_info = None

    if req.image_url:
        downloaded = await download_image_from_url(req.image_url)

        image_info = {
            "content_type": downloaded["content_type"],
            "size_bytes": downloaded["size"],
        }

    return {
        "status": "received",
        "session_id": session_id,
        "message": req.message,
        "image_url": req.image_url,
        "image_path": req.image_path,
        "has_image": req.image_url is not None,
        "image_info": image_info,
    }