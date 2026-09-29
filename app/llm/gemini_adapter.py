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
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
        except Exception as e:
            raise Exception(f"Failed to generate hint: {str(e)}")
