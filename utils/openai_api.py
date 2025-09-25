import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def ask_openai(messages: list, model="gpt-4o-mini") -> str:
    response = await client.chat.completions.create(
        messages=messages,
        model=model,
     )
    answer = response.choices[0].message.content.strip()
    
    return answer