import requests
from django.conf import settings

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def ask_gemini(prompt):
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": settings.GEMINI_API_KEY,
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    response = requests.post(GEMINI_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        try:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError):
            return "No response from Gemini."
    else:
        return f"Error {response.status_code}: {response.text}"
