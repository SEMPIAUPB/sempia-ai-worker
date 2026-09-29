from app.llm.gemini_adapter import GeminiAdapter
from app.common.schemas import TutoringRequest, TutoringResponse

class TutoringService:
    def __init__(self):
        self.llm = GeminiAdapter()

    def generate_hint(self, request: TutoringRequest) -> TutoringResponse:
        # Enforce progressive hinting limit
        if len(request.previous_hints) >= 5:
            return TutoringResponse(
                probable_error_type="Limit reached",
                cause_explanation="You have reached the maximum number of hints for this exercise.",
                programming_concept="N/A",
                pedagogical_recommendation="Please review the material or ask an instructor.",
                confidence_level="High",
                hint_text="Maximum of 5 hints reached. No more hints can be generated.",
                can_resubmit=False
            )

        prompt = f"""
        Act as an expert programming tutor.
        The student is solving the following exercise:
        {request.exercise_statement}
        
        Student's code in {request.language}:
        {request.student_code}
        
        The judge gave the verdict: {request.judge_verdict}
        Compiler/Runtime messages: {request.compiler_or_runtime_messages}
        Failed test cases: {request.failed_test_cases}
        
        Previous hints given to the student: {request.previous_hints}
        
        Generate a JSON response with the following schema:
        {{
            "probable_error_type": "string",
            "approximate_line": "string or null",
            "cause_explanation": "string",
            "programming_concept": "string",
            "pedagogical_recommendation": "string",
            "confidence_level": "string",
            "hint_text": "string",
            "can_resubmit": boolean
        }}
        
        Rules for hint_text:
        - Do not give the full solution.
        - Give a progressive hint. Since there were {len(request.previous_hints)} previous hints, make this hint slightly more specific than the last one, but still educational.
        """
        
        try:
            response_data = self.llm.generate_tutoring_hint(prompt)
            return TutoringResponse(**response_data)
        except Exception as e:
            raise Exception(f"Tutoring service failed: {str(e)}")
