"""Helpers for validating API search filters and cleaning judgment text."""

from datetime import datetime
from html import unescape
import re

from fastapi import HTTPException


COURT_DOCTYPES = {
    "supreme court": "supremecourt",
    "delhi high court": "delhi",
    "bombay high court": "bombay",
    "madras high court": "chennai",
    "calcutta high court": "kolkata",
    "kerala high court": "kerala",
    "all high courts": "highcourts",
}


def normalize_date(value: str | None) -> str | None:
    """Validate a user date and return Indian Kanoon's accepted D-M-YYYY form."""
    if value is None:
        return None
    try:
        parsed = datetime.strptime(value, "%d-%m-%Y")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Dates must use DD-MM-YYYY format.") from exc
    return f"{parsed.day}-{parsed.month}-{parsed.year}"


def build_search_query(
    query: str,
    court: str | None,
    fromdate: str | None,
    todate: str | None,
) -> str:
    """Add documented Indian Kanoon filters to a user query safely."""
    terms = [query.strip()]
    if court:
        doctype = COURT_DOCTYPES.get(court.casefold())
        if not doctype:
            raise HTTPException(status_code=422, detail="Unsupported court filter.")
        terms.append(f"doctypes:{doctype}")
    if fromdate:
        terms.append(f"fromdate:{fromdate}")
    if todate:
        terms.append(f"todate:{todate}")
    return " ".join(terms)


def clean_judgment_text(value: object) -> str:
    """Remove HTML while retaining paragraph boundaries for passage chunking."""
    if value is None:
        return ""
    text = str(value)
    text = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", text)
    text = re.sub(r"(?i)<br\s*/?>|</(?:p|div|li|tr|h[1-6])\s*>", "\n", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text).replace("\xa0", " ")
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)
