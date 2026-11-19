from groq import Groq

client = Groq(
    api_key="ضع مفتاحك هنا"
)

response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {
            "role": "user",
            "content": "اكتب كلمة مرحبا فقط"
        }
    ]
)

print(response.choices[0].message.content)