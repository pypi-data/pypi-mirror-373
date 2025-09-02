import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load variables from .env if present
load_dotenv()

# Try to get API key from environment
_api_key = os.getenv("CHILLAX_API_KEY")

if _api_key:
    genai.configure(api_key=_api_key)
else:
    raise RuntimeError(
        "API key not found. Please set CHILLAX_API_KEY in a .env file or as an environment variable."
    )

def _ask(prompt: str) -> str:
    """Send a query to Gemini and return the response."""
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text

class Chillax:
    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            return _ask(f"Perform `{name}` with args={args}, kwargs={kwargs} , just give the answer do not explain")
        return wrapper

chillax = Chillax()
