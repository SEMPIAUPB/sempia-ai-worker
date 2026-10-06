import google.generativeai as genai
import json
from app.common.config import settings

# Initialize Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

class GeminiAdapter:
    def __init__(self):
        self.model_id = settings.GEMINI_MODEL_ID
        try:
            self.model = genai.GenerativeModel(self.model_id)
        except Exception:
            self.model = None

    def generate_tutoring_hint(self, prompt: str) -> dict:
        if not self.model:
            raise Exception("Gemini model not initialized properly.")
            
        try:
            # We enforce JSON response structure using the prompt
            response = self.model.generate_content(
                prompt,
                generation_config={"temperature": 0.2}
            )
            # Clean possible markdown formatting
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            
            return json.loads(text.strip())
        except Exception as e:
            raise Exception(f"Failed to generate hint: {str(e)}")
