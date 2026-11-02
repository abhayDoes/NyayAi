"""Bounded keyword retrieval and passage ranking over Indian Kanoon results."""

from datetime import datetime
import re
from typing import Any

from fastapi import HTTPException

from app.config import get_settings
from app.schemas.retrieval import (
    RetrievedJudgment,
    RetrievedPassage,
    RetrievalRequest,
    RetrievalResponse,
)
from app.services.indian_kanoon import IndianKanoonClient, IndianKanoonError
from app.utils.helpers import build_search_query, clean_judgment_text, normalize_date


STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "by", "for", "from",
    "had", "has", "have", "he", "her", "his", "in", "into", "is", "it", "its",
    "of", "on", "or", "our", "she", "that", "the", "their", "them", "there",
    "this", "to", "was", "were", "with", "who", "will", "would",
}
TOKEN_PATTERN = re.compile(r"[a-z0-9]{3,}", re.IGNORECASE)
CHUNK_WORDS = 900
CHUNK_OVERLAP = 120


def _terms(text: str) -> set[str]:
    return {token.casefold() for token in TOKEN_PATTERN.findall(text) if token.casefold() not in STOP_WORDS}


def _rank_text(text: str, terms: set[str]) -> tuple[float, list[str]]:
    if not terms:
        return 0.0, []
    present = sorted(term for term in terms if re.search(rf"\b{re.escape(term)}\b", text, re.IGNORECASE))
    return round(len(present) / len(terms), 4), present


def _chunks(text: str) -> list[str]:
    words = text.split()
    if not words:
        return []
    chunks = []
    step = CHUNK_WORDS - CHUNK_OVERLAP
    for start in range(0, len(words), step):
        chunk = " ".join(words[start : start + CHUNK_WORDS]).strip()
        if chunk:
            chunks.append(chunk)
        if start + CHUNK_WORDS >= len(words):
            break
    return chunks


def _metadata(doc: dict[str, Any], document_id: str) -> dict[str, Any]:
    return {
        "document_id": str(doc.get("tid") or doc.get("docid") or document_id),
        "case_name": clean_judgment_text(doc.get("title")) or "Title unavailable",
        "court": clean_judgment_text(doc.get("docsource")) or None,
        "judgment_date": clean_judgment_text(doc.get("date") or doc.get("judgment_date")) or None,
        "case_number": clean_judgment_text(doc.get("case_number") or doc.get("caseno")) or None,
        "source_url": f"https://indiankanoon.org/doc/{document_id}/",
    }


class KeywordRetrievalService:
    """Search user-approved queries, fetch a bounded set of documents, rank evidence."""

    async def retrieve(self, request: RetrievalRequest) -> RetrievalResponse:
        if request.fromdate and request.todate:
            from_date = normalize_date(request.fromdate)
            to_date = normalize_date(request.todate)
            if from_date and to_date:
                from_datetime = datetime.strptime(from_date, "%d-%m-%Y")
                to_datetime = datetime.strptime(to_date, "%d-%m-%Y")
                if from_datetime > to_datetime:
                    raise HTTPException(status_code=422, detail="fromdate must be on or before todate.")

        queries = [query.strip() for query in request.search_queries if query.strip()]
        if not queries:
            raise HTTPException(status_code=422, detail="At least one non-empty search query is required.")

        client = IndianKanoonClient(get_settings().indian_kanoon_timeout_seconds)
        warnings: list[str] = []
        candidates: dict[str, dict[str, Any]] = {}
        searched_queries: list[str] = []

        # Sequential requests make API usage predictable and avoid request bursts.
        for query in queries:
            filtered_query = build_search_query(
                query,
                request.court,
                normalize_date(request.fromdate),
                normalize_date(request.todate),
            )
            try:
                data = await client.search(filtered_query, 0)
            except IndianKanoonError as error:
                if "not configured" in str(error) or "rejected" in str(error):
                    raise HTTPException(status_code=503, detail=str(error)) from error
                warnings.append(f"Search request could not be completed for: {query}")
                continue
            searched_queries.append(query)
            docs = data.get("docs", [])
            if not isinstance(docs, list):
                warnings.append(f"Search response was invalid for: {query}")
                continue
            for doc in docs:
                if not isinstance(doc, dict):
                    continue
                doc_id = doc.get("tid") or doc.get("docid")
                if doc_id is not None and str(doc_id).isdigit():
                    candidates.setdefault(str(doc_id), doc)

        if not searched_queries and warnings:
            raise HTTPException(status_code=502, detail="All Indian Kanoon search requests failed.")
        if not candidates:
            return RetrievalResponse(searched_queries=searched_queries, judgments=[], warnings=warnings)

        case_terms = _terms(" ".join(request.facts + request.legal_issues + queries))
        initially_ranked = sorted(
            candidates.items(),
            key=lambda item: _rank_text(
                " ".join(str(item[1].get(key) or "") for key in ("title", "headline", "snippet", "docsource")),
                case_terms,
            )[0],
            reverse=True,
        )[: request.max_judgments]

        judgments: list[RetrievedJudgment] = []
        for document_id, search_doc in initially_ranked:
            try:
                document = await client.get_document(document_id)
            except IndianKanoonError:
                warnings.append(f"Full text was unavailable for document {document_id}.")
                continue
            text = clean_judgment_text(document.get("doc"))
            if not text:
                warnings.append(f"Full text was empty for document {document_id}.")
                continue

            merged_metadata = {**search_doc, **document}
            passages = []
            for chunk in _chunks(text):
                score, matched_terms = _rank_text(chunk, case_terms)
                if score > 0:
                    passages.append(
                        RetrievedPassage(text=chunk, keyword_score=score, matched_terms=matched_terms)
                    )
            passages.sort(key=lambda passage: passage.keyword_score, reverse=True)
            passages = passages[: request.passages_per_judgment]
            if not passages:
                warnings.append(f"No keyword-matched passage was found in document {document_id}.")
            best_score = passages[0].keyword_score if passages else _rank_text(text[:5000], case_terms)[0]
            best_matches = passages[0].matched_terms if passages else []
            judgments.append(
                RetrievedJudgment(
                    **_metadata(merged_metadata, document_id),
                    keyword_score=best_score,
                    matched_terms=best_matches,
                    passages=passages,
                )
            )

        judgments.sort(key=lambda judgment: judgment.keyword_score, reverse=True)
        return RetrievalResponse(
            searched_queries=searched_queries,
            judgments=judgments,
            warnings=warnings,
        )
