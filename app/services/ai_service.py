import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def get_ai_response(user_message):
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": (
                    "Sen ALVÉRA cilt bakım markasının yapay zekâ asistanısın. "
                    "Kullanıcılara ürünler, cilt bakım rutinleri ve ALVÉRA hakkında "
                    "nazik, kısa ve anlaşılır yanıtlar ver."
                )
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
    )

    return completion.choices[0].message.content