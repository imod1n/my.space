// frontend/src/stores/budget.js
// Изолированный Pinia store для раздела личного бюджета.
// Не импортирует и не изменяет payments store.

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as api from '../api/budget'

export const useBudgetStore = defineStore('budget', () => {

  // ── Auth state ─────────────────────────────────────────────────────────────
  const userId   = ref(sessionStorage.getItem('budget_user_id') || '')
  const userName = ref(sessionStorage.getItem('budget_user_name') || '')
  const isAuthenticated = ref(!!sessionStorage.getItem('budget_token'))

  // ── Data ───────────────────────────────────────────────────────────────────
  const accounts      = ref([])   // AccountOut[]
  const periods       = ref([])   // PeriodOut[] sorted desc
  const currentPeriod = ref(null) // PeriodOut currently viewed
  const balances      = ref([])   // BalanceOut[] for currentPeriod
  const income        = ref([])   // IncomeOut[]
  const transfers     = ref([])   // TransferOut[]
  const loading       = ref(false)
  const error         = ref('')

  // ── Computed ───────────────────────────────────────────────────────────────
  const accountsWithBalances = computed(() =>
    accounts.value.map(acc => {
      const bal = balances.value.find(b => b.account_id === acc.id)
      const start   = bal?.balance_start   ?? 0
      const current = bal?.balance_current ?? 0
      return { ...acc, balance_start: start, balance_current: current, delta: current - start }
    })
  )

  const totalStart   = computed(() => accountsWithBalances.value.reduce((s, a) => s + a.balance_start,   0))
  const totalCurrent = computed(() => accountsWithBalances.value.reduce((s, a) => s + a.balance_current, 0))
  const totalIncome   = computed(() => income.value.filter(i => i.category !== 'Аванс').reduce((s, i) => s + i.amount, 0))
  const totalExpenses = computed(() => totalStart.value + totalIncome.value - totalCurrent.value)

  const activePeriod = computed(() => periods.value.find(p => p.is_active) ?? null)
  const isViewingActive = computed(() => currentPeriod.value?.id === activePeriod.value?.id)

  // ── Auth actions ───────────────────────────────────────────────────────────
  async function login(uid, pinHash) {
    const result = await api.budgetAuth(uid, pinHash)
    sessionStorage.setItem('budget_token',     result.token)
    sessionStorage.setItem('budget_user_id',   result.user_id)
    sessionStorage.setItem('budget_user_name', result.name)
    userId.value        = result.user_id
    userName.value      = result.name
    isAuthenticated.value = true
    return result
  }

  function logout() {
    sessionStorage.removeItem('budget_token')
    sessionStorage.removeItem('budget_user_id')
    sessionStorage.removeItem('budget_user_name')
    userId.value = ''; userName.value = ''; isAuthenticated.value = false
    accounts.value = []; periods.value = []; currentPeriod.value = null
    balances.value = []; income.value = []; transfers.value = []
    error.value = ''
  }

  // ── Data loading ───────────────────────────────────────────────────────────
  async function init() {
    if (!isAuthenticated.value) return
    loading.value = true
    error.value   = ''
    try {
      const [accs, perds] = await Promise.all([
        api.getAccounts(userId.value),
        api.getPeriods(userId.value),
      ])
      accounts.value = accs
      periods.value  = perds

      const active = perds.find(p => p.is_active) ?? null
      if (active) {
        currentPeriod.value = active
        await _fetchPeriodData(active.id)
      }
    } catch (e) {
      error.value = e.response?.data?.detail || 'Ошибка загрузки данных'
    } finally {
      loading.value = false
    }
  }

  async function _fetchPeriodData(periodId) {
    const [bals, inc, trans] = await Promise.all([
      api.getBalances(userId.value, periodId),
      api.getIncome(userId.value, periodId),
      api.getTransfers(userId.value, periodId),
    ])
    balances.value  = bals
    income.value    = inc
    transfers.value = trans
  }

  async function switchPeriod(period) {
    currentPeriod.value = period
    loading.value = true
    try {
      await _fetchPeriodData(period.id)
    } finally {
      loading.value = false
    }
  }

  // ── Account actions ────────────────────────────────────────────────────────
  async function addAccount(data) {
    const acc = await api.createAccount(userId.value, data)
    accounts.value.push(acc)

    // Create a zero-balance record for the active period
    if (activePeriod.value) {
      try {
        const bal = await api.setBalance(userId.value, activePeriod.value.id, {
          account_id: acc.id, balance_start: 0, balance_current: 0,
        })
        if (currentPeriod.value?.id === activePeriod.value.id) {
          balances.value.push(bal)
        }
      } catch {
        // Account already saved — balance will be created on next refresh
      }
    }
    return acc
  }

  async function removeAccount(id) {
    await api.deleteAccount(userId.value, id)
    accounts.value  = accounts.value.filter(a => a.id !== id)
    balances.value  = balances.value.filter(b => b.account_id !== id)
  }

  async function reorderAccounts(orderedIds) {
    // Optimistic update
    accounts.value = orderedIds.map((id, i) => {
      const acc = accounts.value.find(a => a.id === id)
      return { ...acc, sort_order: i }
    })
    // Persist each changed sort_order
    await Promise.all(
      orderedIds.map((id, i) => api.updateAccount(userId.value, id, { sort_order: i }))
    )
  }

  // ── Period actions ─────────────────────────────────────────────────────────
  async function startNewPeriod(startDate) {
    const period = await api.createPeriod(userId.value, startDate)
    // Mark previous active as inactive, set end_date = startDate - 1 day (mirrors backend logic)
    const endDt = new Date(startDate)
    endDt.setDate(endDt.getDate() - 1)
    const endDate = endDt.toISOString().slice(0, 10)
    periods.value = periods.value.map(p => p.is_active ? { ...p, is_active: false, end_date: endDate } : p)
    periods.value.unshift(period)
    currentPeriod.value = period
    await _fetchPeriodData(period.id)

    return period
  }

  async function deleteCurrentPeriod() {
    if (!activePeriod.value) return
    const restored = await api.deletePeriod(userId.value, activePeriod.value.id)
    // Remove deleted period from list, mark restored as active
    periods.value = periods.value
      .filter(p => p.id !== activePeriod.value?.id)
      .map(p => p.id === restored.id ? restored : p)
    currentPeriod.value = restored
    await _fetchPeriodData(restored.id)
  }

  // ── Balance actions ────────────────────────────────────────────────────────
  async function updateBalance(accountId, balanceStart, balanceCurrent) {
    if (!currentPeriod.value) return
    const bal = await api.setBalance(userId.value, currentPeriod.value.id, {
      account_id: accountId, balance_start: balanceStart, balance_current: balanceCurrent,
    })
    const idx = balances.value.findIndex(b => b.account_id === accountId)
    if (idx >= 0) balances.value[idx] = bal
    else balances.value.push(bal)
  }

  async function addAdvance(accountId, amount) {
    if (!currentPeriod.value) return
    const bal = await api.addAdvance(userId.value, currentPeriod.value.id, {
      account_id: accountId, amount,
    })
    const idx = balances.value.findIndex(b => b.account_id === accountId)
    if (idx >= 0) balances.value[idx] = bal
    else balances.value.push(bal)
  }

  // ── Income actions ─────────────────────────────────────────────────────────
  async function addIncomeEntry(data) {
    if (!currentPeriod.value) return
    const inc = await api.addIncome(userId.value, currentPeriod.value.id, data)
    income.value.unshift(inc)
  }

  async function removeIncomeEntry(id) {
    await api.deleteIncome(userId.value, id)
    income.value = income.value.filter(i => i.id !== id)
  }

  // ── Transfer actions ───────────────────────────────────────────────────────
  async function addTransferEntry(data) {
    if (!currentPeriod.value) return
    const t = await api.addTransfer(userId.value, currentPeriod.value.id, data)
    transfers.value.unshift(t)
    // Refresh balances (two accounts changed)
    balances.value = await api.getBalances(userId.value, currentPeriod.value.id)
    return t
  }

  async function removeTransferEntry(id) {
    await api.deleteTransfer(userId.value, id)
    transfers.value = transfers.value.filter(t => t.id !== id)
    if (currentPeriod.value) {
      balances.value = await api.getBalances(userId.value, currentPeriod.value.id)
    }
  }

  return {
    // state
    userId, userName, isAuthenticated,
    accounts, periods, currentPeriod,
    balances, income, transfers,
    loading, error,
    // computed
    accountsWithBalances, activePeriod, isViewingActive,
    totalStart, totalCurrent, totalIncome, totalExpenses,
    // actions
    login, logout, init, switchPeriod,
    addAccount, removeAccount, reorderAccounts,
    startNewPeriod, deleteCurrentPeriod,
    updateBalance, addAdvance,
    addIncomeEntry, removeIncomeEntry,
    addTransferEntry, removeTransferEntry,
  }
})
