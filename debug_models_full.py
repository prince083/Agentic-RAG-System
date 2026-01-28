import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

print("Listing ALL available models and their methods...")
try:
    with open("available_models.txt", "w", encoding="utf-8") as f:
        for m in genai.list_models():
            f.write(f"Name: {m.name}\n")
            f.write(f"Supported methods: {m.supported_generation_methods}\n")
            f.write("-" * 20 + "\n")
except Exception as e:
    print("Error listing models:", e)
