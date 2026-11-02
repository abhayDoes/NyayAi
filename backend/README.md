# NyayaAI backend foundation

This phase provides the FastAPI service, SQLite session setup, initial research
and judgment tables, environment-based configuration, CORS, and a health route.
The judgment and research tables are empty; no sample judgments are included.

## Indian Kanoon API

`GET /api/search/judgments?query=...` returns one zero-based page of source
results. Optional filters are `court`, `fromdate`, and `todate` (dates use
`DD-MM-YYYY`). `GET /api/judgments/{document_id}` retrieves full text only when
requested. Both routes preserve Indian Kanoon's document ID and original public
document URL. Results can have missing dates or case numbers because those are
not present in every search response.

Indian Kanoon charges per request. Search results are not cached by this
backend; each search page and opened document causes an API request. Add clear
"powered by IKanoon" attribution in the user interface before displaying data,
as required by Indian Kanoon's terms.

## Case description analysis

`POST /api/research/analyze` accepts a case description and returns a validated
category, facts, legal issues, legal terminology, and search phrases. It sends
the description to the configured chat-completions-compatible LLM. The backend
does not save the description. Analysis is unavailable until `LLM_API_BASE_URL`,
`LLM_API_KEY`, and `LLM_MODEL` are configured in the backend environment. The
prompt asks the model to extract research inputs only; it does not determine
the merits or assert the current state of Indian law.

## Run locally

From this directory, create and activate a virtual environment, install
`requirements.txt`, copy `.env.example` to `.env`, and start the API:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for Swagger UI. The liveness check is
`GET http://127.0.0.1:8000/api/health`.

Provider credentials belong in the backend `.env` file or deployment secret
store. Never place them in React code or commit `.env`.
