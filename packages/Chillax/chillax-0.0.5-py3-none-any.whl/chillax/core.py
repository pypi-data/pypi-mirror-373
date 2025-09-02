import os
import google.generativeai as genai


def _ask(prompt: str) -> str:
    """Send a query to Gemini and return the response."""
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text



class Chillax:

    @staticmethod
    def setAPIKey(api):
        if api:
            genai.configure(api_key=api)
        else:
            raise RuntimeError(
                "API key not found. please enter the correct api "
            )

    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            return _ask(f"Perform `{name}` with args={args}, kwargs={kwargs} , just give the answer do not explain")
        return wrapper

chillax = Chillax()
