from google import genai

client = genai.Client(
    api_key="aput your api_is_here"
)
response = client.models.generate_content(
    model="gemini-flash-latest",
    contents="اكتب كلمة مرحبا فقط"
)

print(response.text)