const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
export async function fetchJson(path:string){ const r = await fetch(`${API}${path}`, {cache:'no-store'}); return r.json(); }
