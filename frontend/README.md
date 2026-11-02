# NyayaAI frontend

React + Vite interface for the backend research workflow. It contains no
sample judgments: searches, passages, and judgment details come from API
responses.

## Run locally

Use Node.js 20.19+ or 22.12+, install dependencies, copy `.env.example` to
`.env`, then start the Vite server:

```powershell
npm install
Copy-Item .env.example .env
npm run dev
```

Set `VITE_API_BASE_URL` in `.env` if the FastAPI server is not at
`http://127.0.0.1:8000`. Keep provider API keys in the backend environment;
this frontend does not need them. The case description is sent to the
configured LLM provider by the backend when the user requests case analysis.

## Research flow

1. Enter a case description and request analysis.
2. Review and edit facts, legal issues, and search phrases.
3. Search and filter real Indian Kanoon results.
4. Open the source-backed judgment text or compare up to three results.

Animations use CSS and respect `prefers-reduced-motion`.
