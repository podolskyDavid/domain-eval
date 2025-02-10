from dotenv import load_dotenv
import anthropic
import os

load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def get_sonnet35_response(message: str) -> str:
    message = client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=4000,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": message
                    }
                ]
            }
        ]
    )
    return message.content[0].text

def get_haiku35_response(message: str) -> str:
    message = client.messages.create(
        model="claude-3-5-haiku-latest",
        max_tokens=4000,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": message
                    }
                ]
            }
        ]
    )
    return message.content[0].text

if __name__ == "__main__":
    print(get_sonnet35_response("How many stars are in the universe?"))