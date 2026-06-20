import asyncio
from agent.graph import build_graph
async def test_agent():
    graph = build_graph()
    result = await graph.ainvoke({
        "question": "what is biology microbes do a search?",
        "image": None
    })
    print(result)

if __name__ == "__main__":
    asyncio.run(test_agent())