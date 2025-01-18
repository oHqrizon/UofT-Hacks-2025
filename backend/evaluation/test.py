import os

from groq import Groq

client = Groq(
    api_key= "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",
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": f'{question}'
        }
    ],
    model="llama3-70b-8192",
)

print(chat_completion.choices[0].message.content)