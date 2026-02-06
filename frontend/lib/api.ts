'use client'

import { authStore } from './auth'

export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api'

async function refreshAccess() {
  const refresh = authStore.getRefresh()
  if (!refresh) return ''
  const r = await fetch(`${API_BASE}/auth/token/refresh/`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ refresh })
  })
  if (!r.ok) return ''
  const data = await r.json()
  authStore.setTokens({ access: data.access, refresh })
  return data.access as string
}

export async function apiFetch<T>(path: string, init?: RequestInit, auth = true): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json', ...(init?.headers as Record<string, string> || {}) }
  if (auth) {
    const token = authStore.getAccess()
    if (token) headers.Authorization = `Bearer ${token}`
  }
  let res = await fetch(`${API_BASE}${path}`, { ...init, headers })
  if (res.status === 401 && auth) {
    const next = await refreshAccess()
    if (next) {
      headers.Authorization = `Bearer ${next}`
      res = await fetch(`${API_BASE}${path}`, { ...init, headers })
    }
  }
  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `Request failed: ${res.status}`)
  }
  return res.json() as Promise<T>
}
