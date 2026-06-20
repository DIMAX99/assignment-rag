from typing import Optional
from pydantic import BaseModel, Field


class AgentState(BaseModel):
    # ── Input ──────────────────────────────────────────────────────────────
    question:   str            = Field(..., description="Raw user question")
    image_url:  Optional[str]  = Field(None, description="Optional image URL")

    # ── Gate ───────────────────────────────────────────────────────────────
    gate_decision: Optional[str] = Field(None, description='"allow" or "block"')
    gate_reason:   Optional[str] = Field(None, description="One-line explanation from gate LLM")

    # ── Image ──────────────────────────────────────────────────────────────
    image_summary: Optional[str] = Field(None, description="Visual analysis of the uploaded image")

    # ── Retrieval ──────────────────────────────────────────────────────────
    search_query:      Optional[str]  = Field(None, description="Refined query sent to the vector store")
    retrieved_context: Optional[str]  = Field(None, description="Textbook chunks (and optionally web results)")
    low_similarity:    bool           = Field(False, description="True when retrieved chunks scored below threshold")

    # ── Web search ─────────────────────────────────────────────────────────
    used_web_fallback:  bool           = Field(False, description="Whether web search was triggered")
    web_search_results: Optional[str]  = Field(None, description="Raw Tavily results")

    # ── Output ─────────────────────────────────────────────────────────────
    final_answer: Optional[str] = Field(None, description="Final answer shown to the student")