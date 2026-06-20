import asyncio
from agent.graph import app_graph

async def main():
    result = await app_graph.ainvoke({
        "question": "what is Overharvesting?",
        "image_url": None
    })
    print(result["final_answer"])

asyncio.run(main())