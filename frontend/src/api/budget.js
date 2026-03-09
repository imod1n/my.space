// frontend/src/api/budget.js
// Изолированный API-клиент для раздела личного бюджета.
// Токен берётся из sessionStorage и подставляется автоматически.

import axios from 'axios'

const headers = {}
if (import.meta.env.VITE_API_KEY) {
  headers['X-API-Key'] = import.meta.env.VITE_API_KEY
}

const http = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers,
})

// Attach Bearer token to every request
http.interceptors.request.use(config => {
  const token = sessionStorage.getItem('budget_token')
  if (token) config.headers['Authorization'] = `Bearer ${token}`
  return config
})

const d = r => r.data

// ── Auth ──────────────────────────────────────────────────────────────────────
export const budgetAuth = (user_id, pin_hash) =>
  http.post('/api/budget/auth', { user_id, pin_hash }).then(d)

// ── Accounts ──────────────────────────────────────────────────────────────────
export const getAccounts    = uid       => http.get(`/api/budget/${uid}/accounts`).then(d)
export const createAccount  = (uid, body) => http.post(`/api/budget/${uid}/accounts`, body).then(d)
export const updateAccount  = (uid, id, body) => http.put(`/api/budget/${uid}/accounts/${id}`, body).then(d)
export const deleteAccount  = (uid, id) => http.delete(`/api/budget/${uid}/accounts/${id}`).then(d)

// ── Periods ───────────────────────────────────────────────────────────────────
export const getPeriods     = uid           => http.get(`/api/budget/${uid}/periods`).then(d)
export const createPeriod   = (uid, start_date) => http.post(`/api/budget/${uid}/periods`, { start_date }).then(d)
export const deletePeriod   = (uid, pid)    => http.delete(`/api/budget/${uid}/periods/${pid}`).then(d)

// ── Balances ──────────────────────────────────────────────────────────────────
export const getBalances    = (uid, pid)       => http.get(`/api/budget/${uid}/periods/${pid}/balances`).then(d)
export const setBalance     = (uid, pid, body) => http.post(`/api/budget/${uid}/periods/${pid}/balances`, body).then(d)
export const addAdvance     = (uid, pid, body) => http.post(`/api/budget/${uid}/periods/${pid}/advance`, body).then(d)

// ── Income ────────────────────────────────────────────────────────────────────
export const getIncome      = (uid, pid)       => http.get(`/api/budget/${uid}/periods/${pid}/income`).then(d)
export const addIncome      = (uid, pid, body) => http.post(`/api/budget/${uid}/periods/${pid}/income`, body).then(d)
export const deleteIncome   = (uid, iid)       => http.delete(`/api/budget/${uid}/income/${iid}`).then(d)

// ── Transfers ─────────────────────────────────────────────────────────────────
export const getTransfers   = (uid, pid)       => http.get(`/api/budget/${uid}/periods/${pid}/transfers`).then(d)
export const addTransfer    = (uid, pid, body) => http.post(`/api/budget/${uid}/periods/${pid}/transfers`, body).then(d)
export const deleteTransfer = (uid, tid)       => http.delete(`/api/budget/${uid}/transfers/${tid}`).then(d)
