"""Routes for preparing a case description for legal research."""

from fastapi import APIRouter, HTTPException

from app.schemas.analysis import CaseAnalysis
from app.schemas.case import CaseAnalysisRequest
from app.services.case_analyzer import CaseAnalysisError, CaseAnalyzer

router = APIRouter(prefix="/api/research", tags=["research"])


@router.post("/analyze", response_model=CaseAnalysis)
async def analyze_case(request: CaseAnalysisRequest) -> CaseAnalysis:
    """Extract structured search inputs without persisting the case text."""
    try:
        return await CaseAnalyzer().analyze(request.description)
    except CaseAnalysisError as error:
        message = str(error)
        status_code = 503 if "not configured" in message else 504 if "timed out" in message else 502
        raise HTTPException(status_code=status_code, detail=message) from error
