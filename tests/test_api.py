from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from app.common.schemas import Interaction

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "dkt_model_loaded" in data

def test_dkt_estimate_cold_start():
    # Empty sequence
    req = {
        "student_id": "stud1",
        "sequence": []
    }
    response = client.post("/dkt/estimate", json=req)
    assert response.status_code == 200
    data = response.json()
    assert len(data["predictions"]) > 0
    # Should fallback to cold start
    assert data["predictions"][0]["mastery_estimation"] == 0.5
    assert data["predictions"][0]["uncertainty"] >= 0.8

def test_dkt_estimate_sequence():
    req = {
        "student_id": "stud1",
        "sequence": [
            {"interaction_id": "i1", "skill_id": "1", "is_correct": True, "timestamp": 12345.0},
            {"interaction_id": "i2", "skill_id": "2", "is_correct": False, "timestamp": 12346.0}
        ]
    }
    response = client.post("/dkt/estimate", json=req)
    assert response.status_code == 200
    data = response.json()
    assert len(data["predictions"]) > 0
    assert data["model_version"] is not None

@patch('app.tutoring.service.GeminiAdapter.generate_tutoring_hint')
def test_tutoring_hint(mock_gen):
    mock_gen.return_value = {
        "probable_error_type": "Syntax",
        "approximate_line": "L3",
        "cause_explanation": "Missing colon",
        "programming_concept": "Syntax rules",
        "pedagogical_recommendation": "Review loop syntax",
        "confidence_level": "High",
        "hint_text": "Check your loop definition.",
        "can_resubmit": False
    }
    
    req = {
        "exercise_statement": "Write a loop",
        "student_code": "for i in range(5)\n print(i)",
        "language": "python",
        "judge_verdict": "COMPILATION_ERROR",
        "compiler_or_runtime_messages": "SyntaxError",
        "failed_test_cases": "[]",
        "previous_hints": []
    }
    response = client.post("/tutoring/hint", json=req)
    assert response.status_code == 200
    data = response.json()
    assert data["probable_error_type"] == "Syntax"
    assert data["hint_text"] == "Check your loop definition."

def test_tutoring_limit_hints():
    req = {
        "exercise_statement": "Write a loop",
        "student_code": "for i in range(5)\n print(i)",
        "language": "python",
        "judge_verdict": "COMPILATION_ERROR",
        "compiler_or_runtime_messages": "SyntaxError",
        "failed_test_cases": "[]",
        "previous_hints": ["h1", "h2", "h3", "h4", "h5"]
    }
    response = client.post("/tutoring/hint", json=req)
    assert response.status_code == 200
    data = response.json()
    assert data["probable_error_type"] == "Limit reached"
    assert data["can_resubmit"] == False
