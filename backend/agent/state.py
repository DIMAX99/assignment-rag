from typing import Optional
from pydantic import BaseModel, ConfigDict


class AgentState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    session_id: Optional[str] = None

    question: str

    image_url: Optional[str] = None
    image_path: Optional[str] = None

    image_summary: Optional[str] = None

    search_query: Optional[str] = None      # ✅ set by build_query_node
    retrieved_context: Optional[str] = None  # ✅ set by retrieve_node

    final_answer: Optional[str] = None
    used_web_fallback: Optional[bool] = None