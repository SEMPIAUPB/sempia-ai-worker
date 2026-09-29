from pydantic import BaseModel, Field
from typing import List, Optional

class Interaction(BaseModel):
    interaction_id: str
    skill_id: str
    is_correct: bool
    timestamp: float
    metadata: Optional[dict] = None

class DKTRequest(BaseModel):
    student_id: str
    sequence: List[Interaction]

class DKTPrediction(BaseModel):
    skill_id: str
    mastery_estimation: float = Field(..., ge=0.0, le=1.0)
    uncertainty: Optional[float] = None

class DKTResponse(BaseModel):
    student_id: str
    predictions: List[DKTPrediction]
    model_version: str

class TutoringRequest(BaseModel):
    exercise_statement: str
    student_code: str
    language: str
    judge_verdict: str
    compiler_or_runtime_messages: str
    failed_test_cases: str
    previous_hints: List[str]

class TutoringResponse(BaseModel):
    probable_error_type: str
    approximate_line: Optional[str] = None
    cause_explanation: str
    programming_concept: str
    pedagogical_recommendation: str
    confidence_level: str
    hint_text: str
    can_resubmit: bool = False
