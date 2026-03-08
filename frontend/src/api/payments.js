// frontend/src/api/payments.js
import axios from 'axios'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
})

export const createPayment   = (data)      => http.post('/api/payments', data).then(r => r.data)
export const getPayments     = (limit=200) => http.get('/api/payments', { params: { limit } }).then(r => r.data)
export const updatePayment   = (id, data)  => http.put(`/api/payments/${id}`, data).then(r => r.data)
export const deletePayment   = (id)        => http.delete(`/api/payments/${id}`).then(r => r.data)
export const getStats        = (period)    => http.get(`/api/stats/${period}`).then(r => r.data)
export const getStatsHistory  = (months=6)  => http.get('/api/stats-history', { params: { months } }).then(r => r.data)
export const deleteAllPayments = ()          => http.delete('/api/payments/all').then(r => r.data)
