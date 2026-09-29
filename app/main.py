from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from app.common.schemas import DKTRequest, DKTResponse, TutoringRequest, TutoringResponse
from app.common.config import settings
from app.knowledge_tracing.service import KnowledgeTracingService
from app.tutoring.service import TutoringService

app = FastAPI(title="SEMPIA AI Worker - Node 3")

# Initialize services
kt_service = KnowledgeTracingService()
tutoring_service = TutoringService()

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "dkt_model_loaded": kt_service.is_loaded,
        "gemini_configured": bool(settings.GEMINI_API_KEY)
    }

@app.post("/dkt/estimate", response_model=DKTResponse)
def estimate_knowledge(request: DKTRequest):
    try:
        predictions = kt_service.estimate_mastery(request.sequence)
        return DKTResponse(
            student_id=request.student_id,
            predictions=predictions,
            model_version=settings.DKT_MODEL_VERSION
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tutoring/hint", response_model=TutoringResponse)
def generate_hint(request: TutoringRequest):
    try:
        response = tutoring_service.generate_hint(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
