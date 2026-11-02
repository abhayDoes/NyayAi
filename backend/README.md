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
