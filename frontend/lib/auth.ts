'use client'

export type TokenPair = { access: string; refresh: string }
const ACCESS = 'wf_access'
const REFRESH = 'wf_refresh'

export const authStore = {
  getAccess: () => (typeof window === 'undefined' ? '' : localStorage.getItem(ACCESS) || ''),
  getRefresh: () => (typeof window === 'undefined' ? '' : localStorage.getItem(REFRESH) || ''),
  setTokens: (tokens: TokenPair) => {
    localStorage.setItem(ACCESS, tokens.access)
    localStorage.setItem(REFRESH, tokens.refresh)
  },
  clear: () => {
    localStorage.removeItem(ACCESS)
    localStorage.removeItem(REFRESH)
  },
}
