"""Judgment search and document retrieval routes."""

import re
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.config import get_settings
from app.schemas.search import JudgmentDocumentResponse, JudgmentSearchResponse, JudgmentSearchResult
from app.services.indian_kanoon import IndianKanoonClient, IndianKanoonError
from app.utils.helpers import build_search_query, clean_judgment_text, normalize_date

router = APIRouter(prefix="/api", tags=["judgments"])

def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    return clean_judgment_text(value) or None


def _map_search_doc(doc: dict[str, Any]) -> JudgmentSearchResult | None:
    doc_id = doc.get("tid") or doc.get("docid")
    if doc_id is None:
        return None
    document_id = str(doc_id)
    size = doc.get("docsize")
    try:
        size = int(size) if size is not None else None
    except (TypeError, ValueError):
        size = None
    return JudgmentSearchResult(
        document_id=document_id,
        case_name=_clean_text(doc.get("title")) or "Title unavailable",
        court=_clean_text(doc.get("docsource")),
        judgment_date=_clean_text(doc.get("date") or doc.get("judgment_date")),
        case_number=_clean_text(doc.get("case_number") or doc.get("caseno")),
        snippet=_clean_text(doc.get("headline") or doc.get("snippet")),
        source_url=f"https://indiankanoon.org/doc/{document_id}/",
        document_size=size,
    )


def _raise_api_error(error: IndianKanoonError) -> None:
    status = 503 if "not configured" in str(error) else 504 if "timed out" in str(error) else 502
    raise HTTPException(status_code=status, detail=str(error)) from error


@router.get("/search/judgments", response_model=JudgmentSearchResponse)
async def search_judgments(
    query: str = Query(min_length=2, max_length=500),
    court: str | None = Query(default=None),
    from_date: str | None = Query(default=None, alias="fromdate"),
    to_date: str | None = Query(default=None, alias="todate"),
    page: int = Query(default=0, ge=0, le=999),
) -> JudgmentSearchResponse:
    """Search judgments; court/date filters use documented IK query syntax."""
    if from_date and to_date:
        start = datetime.strptime(normalize_date(from_date), "%d-%m-%Y")
        end = datetime.strptime(normalize_date(to_date), "%d-%m-%Y")
        if start > end:
            raise HTTPException(status_code=422, detail="fromdate must be on or before todate.")
    search_text = build_search_query(query, court, normalize_date(from_date), normalize_date(to_date))
    client = IndianKanoonClient(get_settings().indian_kanoon_timeout_seconds)
    try:
        data = await client.search(search_text, page)
    except IndianKanoonError as error:
        _raise_api_error(error)

    raw_docs = data.get("docs", [])
    if not isinstance(raw_docs, list):
        raise HTTPException(status_code=502, detail="Indian Kanoon returned invalid search results.")
    results = [_map_search_doc(doc) for doc in raw_docs if isinstance(doc, dict)]
    return JudgmentSearchResponse(
        query=query,
        page=page,
        found=str(data["found"]) if data.get("found") is not None else None,
        results=[result for result in results if result is not None],
    )


@router.get("/judgments/{document_id}", response_model=JudgmentDocumentResponse)
async def get_judgment(document_id: str) -> JudgmentDocumentResponse:
    """Fetch a judgment body only after a user opens a search result."""
    if not re.fullmatch(r"\d+", document_id):
        raise HTTPException(status_code=422, detail="document_id must contain digits only.")
    client = IndianKanoonClient(get_settings().indian_kanoon_timeout_seconds)
    try:
        data = await client.get_document(document_id)
    except IndianKanoonError as error:
        _raise_api_error(error)

    full_text = _clean_text(data.get("doc"))
    if not full_text:
        raise HTTPException(status_code=502, detail="The source returned no judgment text.")
    doc = {
        "tid": data.get("tid", document_id),
        "title": data.get("title"),
        "docsource": data.get("docsource"),
        "docsize": len(full_text),
    }
    result = _map_search_doc(doc)
    if result is None:
        raise HTTPException(status_code=502, detail="The source returned invalid document metadata.")
    return JudgmentDocumentResponse(**result.model_dump(), full_text=full_text)
