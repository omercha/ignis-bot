import os
import openai
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def ask_openai(prompt: str) -> str:
    """
    Sends a user prompt to the OpenAI GPT-4o-mini chat model asynchronously
    and returns the response text.
    """
    
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    
    answer = response.choices[0].message.content.strip()
    return answer