from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
from openai import OpenAI
import os

class PerplexityResponse(BaseModel):
    content: str
    citations: List[str]

load_dotenv()
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

messages = [
    {
        "role": "system",
        "content": (
            "You are an artificial intelligence assistant and you need to "
            "engage in a helpful, detailed, polite conversation with a user."
        ),
    },
    {   
        "role": "user",
        "content": (
            "How many stars are in the universe?"
        ),
    },
]

client = OpenAI(api_key=PERPLEXITY_API_KEY, base_url="https://api.perplexity.ai")


def get_sonar_pro_response(message: str) -> PerplexityResponse:
    messages = [
        {"role": "user", "content": message}
    ]
    response = client.chat.completions.create(model="sonar-pro", messages=messages)
    return PerplexityResponse(content=response.choices[0].message.content, citations=response.citations)

def get_sonar_response(message: str) -> PerplexityResponse:
    messages = [
        {"role": "user", "content": message}
    ]
    response = client.chat.completions.create(model="sonar", messages=messages)
    return PerplexityResponse(content=response.choices[0].message.content, citations=response.citations)

if __name__ == "__main__":
    print(get_sonar_response("How many stars are in the universe?"))