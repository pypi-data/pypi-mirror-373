import asyncio
from hero_base import ContentChunk, Model

model = Model(
    model_name="claude-3-7-sonnet-20250219-thinking",
    api_base="https://api.laozhang.ai/v1",
    api_key="sk-IORgE0ls6xqROAV0F9Af149b0aF1473e9e91C1437483F847",
    context_length=1000000,
    options={
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "get_horoscope",
                    "description": "Get today's horoscope for an astrological sign.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sign": {
                                "type": "string",
                                "description": "An astrological sign like Taurus or Aquarius",
                            },
                        },
                        "required": ["sign"],
                    },
                }
            },
        ],
        "tool_choice": "auto",
        "parallel_tool_calls": False,
    }
)


async def test_model():
    content = ""
    async for chunk in model.chat("今天金牛座的运势如何？", system_prompt="You are a helpful assistant. must give your reason before calling the tool"):
        if isinstance(chunk, ContentChunk):
            content += chunk.content
    print(content)

if __name__ == "__main__":
    asyncio.run(test_model())
