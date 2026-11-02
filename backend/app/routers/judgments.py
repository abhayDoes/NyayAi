"""Judgment search and document retrieval routes."""

import re
from datetime import datetime
from html import unescape
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.config import get_settings
from app.schemas.search import JudgmentDocumentResponse, JudgmentSearchResponse, JudgmentSearchResult
from app.services.indian_kanoon import IndianKanoonClient, IndianKanoonError

router = APIRouter(prefix="/api", tags=["judgments"])

# Values follow the court doctypes documented by Indian Kanoon. The allowlist
# keeps filter values from injecting arbitrary search operators.
COURT_DOCTYPES = {
    "supreme court": "supremecourt",
    "delhi high court": "delhi",
    "bombay high court": "bombay",
    "madras high court": "chennai",
    "calcutta high court": "kolkata",
    "kerala high court": "kerala",
    "all high courts": "highcourts",
}


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = unescape(re.sub(r"<[^>]+>", " ", str(value)))
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def _search_query(query: str, court: str | None, from_date: str | None, to_date: str | None) -> str:
    terms = [query.strip()]
    if court:
        doctype = COURT_DOCTYPES.get(court.casefold())
        if not doctype:
            raise HTTPException(status_code=422, detail="Unsupported court filter.")
        terms.append(f"doctypes:{doctype}")
    if from_date:
        terms.append(f"fromdate:{from_date}")
    if to_date:
        terms.append(f"todate:{to_date}")
    return " ".join(terms)


def _validate_date(value: str | None) -> str | None:
    if value is None:
        return None
    try:
        parsed = datetime.strptime(value, "%d-%m-%Y")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Dates must use DD-MM-YYYY format.") from exc
    return f"{parsed.day}-{parsed.month}-{parsed.year}"


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
        start = datetime.strptime(_validate_date(from_date), "%d-%m-%Y")
        end = datetime.strptime(_validate_date(to_date), "%d-%m-%Y")
        if start > end:
            raise HTTPException(status_code=422, detail="fromdate must be on or before todate.")
    search_text = _search_query(query, court, _validate_date(from_date), _validate_date(to_date))
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
