const API_BASE = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '');

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: { 'Content-Type': 'application/json', ...options.headers },
    });
  } catch {
    throw new Error(`Can't reach the NyayaAI backend at ${API_BASE}. Start the API and try again.`);
  }

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = payload.detail;
    throw new Error(Array.isArray(detail) ? detail.map((item) => item.msg).join(', ') : detail || `Request failed (${response.status}).`);
  }
  return payload;
}

export function analyzeCase(description) {
  return request('/api/research/analyze', {
    method: 'POST',
    body: JSON.stringify({ description }),
  });
}

export function retrieveJudgments(filters) {
  return request('/api/research/retrieve', {
    method: 'POST',
    body: JSON.stringify(filters),
  });
}

export function getJudgment(documentId) {
  return request(`/api/judgments/${encodeURIComponent(documentId)}`);
}
