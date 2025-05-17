
import google.generativeai as genai

GEMINI_API_KEY = "AIzaSyCUip9wIsYEiN-d-3qbRfSVd9kQZPEnOz8"
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

def ask_gemini(prompt: str) -> str:
    response = model.generate_content(prompt)
    return response.text.strip()
