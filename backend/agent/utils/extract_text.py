# agent/utils/extract_text.py

def extract_text(response_content) -> str:
    if isinstance(response_content, list):
        return " ".join(
            block["text"] for block in response_content
            if isinstance(block, dict) and block.get("type") == "text"
        ).strip()
    return response_content.strip()