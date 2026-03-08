// frontend/src/stores/payments.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as api from '../api/payments'

export const OBJECTS = [
  { name: 'Квартира 1',    icon: '🏠' },
  { name: 'Квартира 2',    icon: '🏢' },
  { name: 'Загородный дом', icon: '🏡' },
  { name: 'Пляжный домик', icon: '🏖️' },
]

export const CATEGORIES = [
  { name: 'Коммунальные',  icon: '🏘️', color: '#0a84ff' },
  { name: 'Электричество', icon: '⚡', color: '#ffd60a' },
  { name: 'Интернет',      icon: '🌐', color: '#bf5af2' },
  { name: 'Телевидение',   icon: '📺', color: '#30d158' },
  { name: 'Мусор',         icon: '🗑️', color: '#636366' },
  { name: 'Членские',      icon: '🪪', color: '#ff9f0a' },
  { name: 'Уборка снега',  icon: '❄️', color: '#5ac8fa' },
  { name: 'Прочее',        icon: '📎', color: '#8e8e93' },
]

export function getCatMeta(name) {
  return CATEGORIES.find(c => c.name === name) || { icon: '📋', color: '#8e8e93' }
}

export function getObjMeta(name) {
  return OBJECTS.find(o => o.name === name) || { icon: '🏠' }
}

export const usePaymentsStore = defineStore('payments', () => {
  // ── state ──────────────────────────────────────────────────
  const payments      = ref([])
  const stats         = ref(null)   // { total, by_category, by_object }
  const history       = ref([])
  const historyFull   = ref([])     // all available months for year-over-year chart
  const loading       = ref(false)
  const currentPeriod = ref(todayPeriod())   // YYYY-MM (billing month shown)

  // ── helpers ────────────────────────────────────────────────
  function todayPeriod() {
    const d = new Date()
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
  }

  function prevMonthPeriod() {
    const d = new Date()
    d.setMonth(d.getMonth() - 1)
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
  }

  // ── computed ───────────────────────────────────────────────
  const currentPeriodLabel = computed(() => {
    const [y, m] = currentPeriod.value.split('-')
    const months = ['Январь','Февраль','Март','Апрель','Май','Июнь',
                    'Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь']
    return months[parseInt(m) - 1] + ' ' + y
  })

  // ── navigation ─────────────────────────────────────────────
  function changeMonth(dir) {
    const [y, m] = currentPeriod.value.split('-').map(Number)
    const d = new Date(y, m - 1 + dir, 1)
    currentPeriod.value = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
    fetchStats()
  }

  // ── API calls ──────────────────────────────────────────────
  async function fetchStats() {
    loading.value = true
    try {
      stats.value = await api.getStats(currentPeriod.value)
    } finally {
      loading.value = false
    }
  }

  async function fetchPayments() {
    payments.value = await api.getPayments()
  }

  async function fetchHistory() {
    history.value = await api.getStatsHistory(6)
  }

  async function fetchHistoryFull() {
    historyFull.value = await api.getStatsHistory(36)
  }

  async function addPayment(data) {
    // data: { category, object_name, amount, date, period, note }
    await api.createPayment(data)
    await fetchStats()
    await fetchPayments()
  }

  async function updatePayment(id, data) {
    await api.updatePayment(id, data)
    await fetchStats()
    await fetchPayments()
  }

  async function deletePayment(id) {
    await api.deletePayment(id)
    await fetchStats()
    await fetchPayments()
  }

  // ── init ───────────────────────────────────────────────────
  async function init() {
    currentPeriod.value = todayPeriod()
    await Promise.all([fetchStats(), fetchPayments(), fetchHistory(), fetchHistoryFull()])
  }

  return {
    payments, stats, history, historyFull, loading,
    currentPeriod, currentPeriodLabel,
    changeMonth, fetchStats, fetchPayments, fetchHistory, fetchHistoryFull,
    addPayment, updatePayment, deletePayment, init,
    prevMonthPeriod, todayPeriod,
  }
})
