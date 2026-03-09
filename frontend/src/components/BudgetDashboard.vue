<template>
  <div class="bd-wrap">

    <!-- ── Шапка бюджета ────────────────────────────────────────── -->
    <div class="bd-topbar">
      <div class="bd-user">
        <span class="bd-user-avatar">{{ store.userName[0] }}</span>
        <span class="bd-user-name">{{ store.userName }}</span>
      </div>
      <button class="bd-logout" @click="store.logout()" title="Выйти">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
          <polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>
        </svg>
      </button>
    </div>

    <!-- ── Загрузка ─────────────────────────────────────────────── -->
    <div v-if="store.loading" class="bd-loading">
      <div class="bd-spinner"></div>
    </div>

    <template v-else>

      <!-- ── Нет периодов: первый запуск ─────────────────────────── -->
      <div v-if="!store.periods.length" class="bd-empty">
        <div class="bd-empty-icon">💰</div>
        <p class="bd-empty-title">Начните первый период</p>
        <p class="bd-empty-sub">Задайте дату начала и добавьте счета</p>
        <button class="bd-btn-primary" @click="openNewPeriod">Начать период</button>
      </div>

      <template v-else>

        <!-- ── Навигация по периодам ────────────────────────────── -->
        <div class="bd-period-nav">
          <button
            class="bd-nav-btn"
            :disabled="periodIdx >= store.periods.length - 1"
            @click="navigate(1)"
          >
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
              <path d="M10 12L6 8L10 4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>

          <span class="bd-period-label">{{ periodLabel(store.currentPeriod) }}</span>

          <button
            class="bd-nav-btn"
            :disabled="periodIdx === 0"
            @click="navigate(-1)"
          >
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
              <path d="M6 4L10 8L6 12" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>

          <button
            v-if="store.isViewingActive"
            class="bd-new-period-btn"
            @click="openNewPeriod"
          >
            <span class="mdi mdi-new-box"></span>
          </button>

          <button
            v-if="store.isViewingActive && store.periods.length > 1"
            class="bd-del-period-btn"
            @click="confirmDeletePeriod"
            title="Удалить текущий период"
          >
            <span class="mdi mdi-delete-empty-outline"></span>
          </button>
        </div>

        <!-- ── Hero card ─────────────────────────────────────────── -->
        <div class="card bd-hero">
          <div class="bd-hero-label">Итого на счетах</div>
          <div class="bd-hero-total">{{ fmt(store.totalCurrent) }}</div>

          <div class="bd-hero-meta">
            <div class="bd-hero-row">
              <span class="bd-meta-key">Начало периода</span>
              <span class="bd-meta-val">{{ fmt(store.totalStart) }}</span>
            </div>
            <div class="bd-hero-row">
              <span class="bd-meta-key">Доходы</span>
              <span class="bd-meta-val" style="color: #30d158">+{{ fmt(store.totalIncome) }}</span>
            </div>
            <div class="bd-hero-row">
              <span class="bd-meta-key">Расходы</span>
              <span
                class="bd-meta-val"
                :style="{ color: store.totalExpenses > 0 ? '#ff453a' : '#30d158' }"
              >{{ store.totalExpenses > 0 ? '-' : '' }}{{ fmt(Math.abs(store.totalExpenses)) }}</span>
            </div>
            <div class="bd-hero-row">
              <span class="bd-meta-key">Остаток за период</span>
              <span
                class="bd-meta-val"
                :style="{ color: store.totalIncome - store.totalExpenses >= 0 ? '#30d158' : '#ff453a' }"
              >{{ store.totalIncome - store.totalExpenses >= 0 ? '+' : '' }}{{ fmt(store.totalIncome - store.totalExpenses) }}</span>
            </div>
          </div>
        </div>

        <!-- ── Счета ─────────────────────────────────────────────── -->
        <div class="card">
          <div class="bd-section-header">
            <span class="bd-section-title">Счета</span>
            <button v-if="store.isViewingActive" class="bd-add-btn" @click="openAddAccount">
              <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
                <line x1="8" y1="2" x2="8" y2="14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <line x1="2" y1="8" x2="14" y2="8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
              Счёт
            </button>
          </div>

          <div v-if="!store.accounts.length" class="bd-empty-sub" style="padding: 8px 0">
            Добавьте первый счёт
          </div>

          <div
            v-for="(acc, idx) in store.accountsWithBalances"
            :key="acc.id"
            class="bd-account-card"
            :class="{
              'bd-drag-over': dragOverIdx === idx,
              'bd-dragging':  draggingIdx === idx,
            }"
            :draggable="store.isViewingActive && store.accounts.length >= 2"
            :data-acc-idx="idx"
            @click="store.isViewingActive && openBalanceSheet(acc)"
            :style="{ cursor: store.isViewingActive ? 'pointer' : 'default' }"
            @dragstart="onDragStart($event, idx)"
            @dragover.prevent="onDragOver(idx)"
            @dragleave="onDragLeave"
            @drop.prevent="onDrop"
            @dragend="onDragEnd"
            @touchstart.passive="onTouchStart($event, idx)"
            @touchmove.prevent="onTouchMove"
            @touchend="onTouchEnd"
          >
            <span
              v-if="store.isViewingActive && store.accounts.length >= 2"
              class="bd-drag-handle"
              @click.stop
            >⠿</span>
            <div class="bd-acc-content">
              <div class="bd-acc-main">
                <span class="bd-acc-icon">{{ typeMeta(acc.type).icon }}</span>
                <span class="bd-acc-name">{{ acc.name }}</span>
              </div>
              <div class="bd-acc-balances">
                <span class="bd-bal-start">{{ fmt(acc.balance_start) }}</span>
                <span class="bd-bal-arrow">→</span>
                <span class="bd-bal-current">{{ fmt(acc.balance_current) }}</span>
              </div>
            </div>
            <button
              v-if="store.isViewingActive && store.accounts.length >= 2"
              class="bd-transfer-btn"
              @click.stop="openTransfer(acc.id)"
              title="Перевод с этого счёта"
            ><span class="mdi mdi-swap-horizontal"></span></button>
          </div>
        </div>

        <!-- ── Доходы ─────────────────────────────────────────────── -->
        <div class="card">
          <div class="bd-section-header">
            <span class="bd-section-title">Доходы</span>
            <button v-if="store.isViewingActive" class="bd-add-btn" @click="openAddIncome">
              <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
                <line x1="8" y1="2" x2="8" y2="14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <line x1="2" y1="8" x2="14" y2="8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
              Доход
            </button>
          </div>

          <div v-if="!store.income.length" class="bd-empty-sub" style="padding: 8px 0">
            Нет записей
          </div>

          <div v-for="inc in store.income" :key="inc.id" class="bd-list-row">
            <div class="bd-row-left">
              <span class="bd-row-date">{{ fmtDate(inc.date) }}</span>
              <span class="bd-row-label">
                {{ inc.category }}
                <span v-if="inc.category === 'Аванс'" class="bd-advance-badge">→ след. период</span>
              </span>
              <span v-if="inc.note" class="bd-row-note">{{ inc.note }}</span>
            </div>
            <div class="bd-row-right">
              <span class="bd-row-amount" :style="{ color: inc.category === 'Аванс' ? '#ff9f0a' : '#30d158' }">+{{ fmt(inc.amount) }}</span>
              <button
                v-if="store.isViewingActive"
                class="bd-del-btn"
                @click="confirmDeleteIncome(inc.id)"
              ><span class="mdi mdi-delete-empty-outline"></span></button>
            </div>
          </div>
        </div>

        <!-- ── Переводы ───────────────────────────────────────────── -->
        <div class="card" v-if="store.transfers.length || (store.isViewingActive && store.accounts.length >= 2)">
          <div class="bd-section-header">
            <span class="bd-section-title">Переводы</span>
            <button
              v-if="store.isViewingActive && store.accounts.length >= 2"
              class="bd-add-btn"
              @click="openTransfer(null)"
            >
              <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
                <line x1="8" y1="2" x2="8" y2="14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                <line x1="2" y1="8" x2="14" y2="8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
              Перевод
            </button>
          </div>

          <div v-if="!store.transfers.length" class="bd-empty-sub" style="padding: 8px 0">Нет переводов</div>

          <div v-for="t in store.transfers" :key="t.id" class="bd-list-row">
            <div class="bd-row-left">
              <span class="bd-row-date">{{ fmtDate(t.date) }}</span>
              <span class="bd-row-label">
                {{ accountName(t.from_account_id) }} → {{ accountName(t.to_account_id) }}
              </span>
            </div>
            <div class="bd-row-right">
              <span class="bd-row-amount" style="color: var(--accent-blue)">{{ fmt(t.amount) }}</span>
              <button
                v-if="store.isViewingActive"
                class="bd-del-btn"
                @click="confirmDeleteTransfer(t.id)"
              ><span class="mdi mdi-delete-empty-outline"></span></button>
            </div>
          </div>
        </div>

      </template><!-- /v-else (has periods) -->
    </template><!-- /v-else (not loading) -->

    <!-- Error banner -->
    <div v-if="store.error" class="bd-error-bar">{{ store.error }}</div>

    <!-- ════════════════════════════════════════════════════════════
         Bottom sheets (rendered via Teleport inside child components)
         ════════════════════════════════════════════════════════════ -->

    <!-- Balance sheet -->
    <BudgetAccountSheet
      v-if="selectedAccount"
      :account="selectedAccount"
      @close="selectedAccount = null"
      @saved="selectedAccount = null"
    />

    <!-- Transfer sheet -->
    <BudgetTransferSheet
      v-if="showTransfer"
      :accounts="store.accounts"
      :preselected="transferPreselected"
      @close="showTransfer = false"
      @saved="showTransfer = false"
    />

    <!-- ── New period sheet ─────────────────────────────────────── -->
    <Teleport to="body">
      <div v-if="showNewPeriod" class="bd-sheet-backdrop" @click.self="showNewPeriod = false">
        <div class="bd-sheet">
          <div class="bd-sheet-header">
            <span class="bd-sheet-title">Новый период</span>
            <button class="bd-sheet-close" @click="showNewPeriod = false">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
          <p class="bd-sheet-info">
            Текущие балансы станут начальными для нового периода.
          </p>
          <div class="bd-field">
            <label class="bd-label">Дата начала</label>
            <input v-model="newPeriodDate" type="date" class="bd-date-input" />
          </div>
          <button class="bd-btn-primary" :disabled="periodSaving" @click="submitNewPeriod">
            {{ periodSaving ? 'Создаю...' : 'Начать период' }}
          </button>
        </div>
      </div>
    </Teleport>

    <!-- ── Add account sheet ───────────────────────────────────── -->
    <Teleport to="body">
      <div v-if="showAddAccount" class="bd-sheet-backdrop" @click.self="showAddAccount = false">
        <div class="bd-sheet">
          <div class="bd-sheet-header">
            <span class="bd-sheet-title">Новый счёт</span>
            <button class="bd-sheet-close" @click="showAddAccount = false">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>

          <div class="bd-field">
            <label class="bd-label">Название</label>
            <input v-model="newAccName" type="text" class="bd-text-input" placeholder="Карта Сбер" />
          </div>

          <div class="bd-field">
            <label class="bd-label">Тип</label>
            <div class="bd-type-grid">
              <button
                v-for="t in ACCOUNT_TYPES" :key="t.type"
                class="bd-type-btn"
                :class="{ active: newAccType === t.type }"
                @click="newAccType = t.type"
              >
                <span>{{ t.icon }}</span>
                <span>{{ t.label }}</span>
              </button>
            </div>
          </div>

          <div v-if="accountError" class="bd-sheet-error">{{ accountError }}</div>

          <button class="bd-btn-primary" :disabled="accountSaving || !newAccName.trim()" @click="submitNewAccount">
            {{ accountSaving ? 'Сохраняю...' : 'Добавить счёт' }}
          </button>
        </div>
      </div>
    </Teleport>

    <!-- ── Add income sheet ────────────────────────────────────── -->
    <Teleport to="body">
      <div v-if="showAddIncome" class="bd-sheet-backdrop" @click.self="showAddIncome = false">
        <div class="bd-sheet">
          <div class="bd-sheet-header">
            <span class="bd-sheet-title">Добавить доход</span>
            <button class="bd-sheet-close" @click="showAddIncome = false">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>

          <div class="bd-field">
            <label class="bd-label">Сумма</label>
            <div class="bd-input-wrap">
              <input v-model="newIncAmount" type="number" inputmode="decimal" class="bd-num-input" placeholder="0" />
              <span class="bd-currency">₽</span>
            </div>
          </div>

          <div class="bd-field">
            <label class="bd-label">Категория</label>
            <div class="bd-cats">
              <button
                v-for="cat in INCOME_CATS" :key="cat"
                class="bd-cat-btn"
                :class="{ active: newIncCategory === cat }"
                @click="newIncCategory = cat"
              >{{ cat }}</button>
            </div>
          </div>

          <div class="bd-field">
            <label class="bd-label">Дата</label>
            <input v-model="newIncDate" type="date" class="bd-date-input" />
          </div>

          <div class="bd-field">
            <label class="bd-label">Примечание</label>
            <input v-model="newIncNote" type="text" class="bd-text-input" placeholder="Необязательно" />
          </div>

          <button
            class="bd-btn-primary"
            :disabled="incomeSaving || !Number(newIncAmount)"
            @click="submitIncome"
          >
            {{ incomeSaving ? 'Сохраняю...' : 'Добавить' }}
          </button>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useBudgetStore } from '../stores/budget'
import BudgetAccountSheet from './BudgetAccountSheet.vue'
import BudgetTransferSheet from './BudgetTransferSheet.vue'

const store = useBudgetStore()

// ── Helpers ──────────────────────────────────────────────────────────────────

const TYPE_META = {
  debit:   { icon: '💳', label: 'Дебетовая карта' },
  credit:  { icon: '💸', label: 'Кредитная карта' },
  savings: { icon: '🏦', label: 'Накопительный' },
  cash:    { icon: '💵', label: 'Наличные' },
  foreign: { icon: '💱', label: 'Иностранный' },
  invest:  { icon: '📈', label: 'Инвестиции' },
  deposit: { icon: '🏛️', label: 'Вклад' },
  other:   { icon: '📂', label: 'Прочее' },
}
const ACCOUNT_TYPES = Object.entries(TYPE_META).map(([type, m]) => ({ type, ...m }))
const INCOME_CATS   = ['Зарплата', 'Аванс', 'Проценты', 'Кэшбек', 'Прочее']

const typeMeta = type => TYPE_META[type] ?? { icon: '💰', label: 'Прочее' }

function fmt(n) { return Math.round(Number(n)).toLocaleString('ru-RU') + ' ₽' }

function fmtDate(str) {
  if (!str) return ''
  const [, m, d] = str.split('-')
  const MONTHS = ['янв','фев','мар','апр','май','июн','июл','авг','сен','окт','ноя','дек']
  return `${parseInt(d)} ${MONTHS[parseInt(m) - 1]}`
}

function periodLabel(p) {
  if (!p) return ''
  const start = fmtDate(p.start_date)
  const end   = p.is_active ? 'сейчас' : fmtDate(p.end_date)
  return `${start} — ${end}`
}

function accountName(id) {
  return store.accounts.find(a => a.id === id)?.name ?? id
}

// ── Period navigation ─────────────────────────────────────────────────────────

const periodIdx = computed(() =>
  store.periods.findIndex(p => p.id === store.currentPeriod?.id)
)

async function navigate(dir) {
  const nextIdx = periodIdx.value + dir
  if (nextIdx < 0 || nextIdx >= store.periods.length) return
  await store.switchPeriod(store.periods[nextIdx])
}

// ── Drag & drop reorder ───────────────────────────────────────────────────────

const draggingIdx = ref(null)
const dragOverIdx = ref(null)
let touchStartIdx = null

function _applyReorder(fromIdx, toIdx) {
  if (fromIdx === toIdx || fromIdx === null || toIdx === null) return
  const ids = store.accountsWithBalances.map(a => a.id)
  const [moved] = ids.splice(fromIdx, 1)
  ids.splice(toIdx, 0, moved)
  store.reorderAccounts(ids)
}

// HTML5 DnD (desktop)
function onDragStart(e, idx) {
  draggingIdx.value = idx
  e.dataTransfer.effectAllowed = 'move'
}
function onDragOver(idx) { dragOverIdx.value = idx }
function onDragLeave()   { dragOverIdx.value = null }
function onDrop()        { _applyReorder(draggingIdx.value, dragOverIdx.value) }
function onDragEnd()     { draggingIdx.value = null; dragOverIdx.value = null }

// Touch (iOS PWA)
function onTouchStart(_e, idx) {
  touchStartIdx = idx
  dragOverIdx.value = idx
}
function onTouchMove(e) {
  const y   = e.touches[0].clientY
  const els = document.elementsFromPoint(e.touches[0].clientX, y)
  const card = els.find(el => el.closest?.('[data-acc-idx]'))
  if (card) {
    const idx = parseInt(card.closest('[data-acc-idx]').dataset.accIdx)
    if (!isNaN(idx)) dragOverIdx.value = idx
  }
}
function onTouchEnd() {
  _applyReorder(touchStartIdx, dragOverIdx.value)
  touchStartIdx = null
  draggingIdx.value = null
  dragOverIdx.value = null
}

// ── Balance sheet ─────────────────────────────────────────────────────────────

const selectedAccount = ref(null)
function openBalanceSheet(acc) { selectedAccount.value = acc }

// ── Transfer sheet ────────────────────────────────────────────────────────────

const showTransfer       = ref(false)
const transferPreselected = ref(null)
function openTransfer(accountId) {
  transferPreselected.value = accountId
  showTransfer.value = true
}

// ── New period sheet ──────────────────────────────────────────────────────────

const showNewPeriod = ref(false)
const periodSaving  = ref(false)
const newPeriodDate = ref(new Date().toISOString().slice(0, 10))

function openNewPeriod() {
  newPeriodDate.value = new Date().toISOString().slice(0, 10)
  showNewPeriod.value = true
}

async function submitNewPeriod() {
  if (!newPeriodDate.value) return
  periodSaving.value = true
  try {
    await store.startNewPeriod(newPeriodDate.value)
    showNewPeriod.value = false
  } finally {
    periodSaving.value = false
  }
}

// ── Add account sheet ─────────────────────────────────────────────────────────

const showAddAccount = ref(false)
const accountSaving  = ref(false)
const accountError   = ref('')
const newAccName     = ref('')
const newAccType     = ref('debit')

function openAddAccount() {
  newAccName.value = ''
  newAccType.value = 'debit'
  accountError.value = ''
  showAddAccount.value = true
}

async function submitNewAccount() {
  if (!newAccName.value.trim()) return
  accountSaving.value = true
  accountError.value = ''
  try {
    await store.addAccount({ name: newAccName.value.trim(), type: newAccType.value, sort_order: store.accounts.length })
    showAddAccount.value = false
  } catch (e) {
    accountError.value = e.response?.data?.detail || 'Ошибка соединения. Попробуйте ещё раз.'
  } finally {
    accountSaving.value = false
  }
}

// ── Add income sheet ──────────────────────────────────────────────────────────

const showAddIncome   = ref(false)
const incomeSaving    = ref(false)
const newIncAmount    = ref('')
const newIncCategory  = ref('Зарплата')
const newIncDate      = ref(new Date().toISOString().slice(0, 10))
const newIncNote      = ref('')

function openAddIncome() {
  newIncAmount.value   = ''
  newIncCategory.value = 'Зарплата'
  newIncDate.value     = new Date().toISOString().slice(0, 10)
  newIncNote.value     = ''
  showAddIncome.value  = true
}

async function submitIncome() {
  if (!Number(newIncAmount.value)) return
  incomeSaving.value = true
  try {
    await store.addIncomeEntry({
      amount:   Number(newIncAmount.value),
      date:     newIncDate.value,
      category: newIncCategory.value,
      note:     newIncNote.value,
    })
    showAddIncome.value = false
  } finally {
    incomeSaving.value = false
  }
}

// ── Delete confirmations ──────────────────────────────────────────────────────

async function confirmDeleteIncome(id) {
  if (!confirm('Удалить запись о доходе?')) return
  await store.removeIncomeEntry(id)
}

async function confirmDeleteTransfer(id) {
  if (!confirm('Удалить перевод? Балансы счетов будут восстановлены.')) return
  await store.removeTransferEntry(id)
}

// ── Delete current period ─────────────────────────────────────────────────────

async function confirmDeletePeriod() {
  if (!confirm('Удалить текущий период? Все данные периода (балансы, доходы, переводы) будут удалены безвозвратно.')) return
  await store.deleteCurrentPeriod()
}

// ── Init ──────────────────────────────────────────────────────────────────────
onMounted(() => store.init())
</script>

<style scoped>
.bd-wrap {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-bottom: 24px;
}

/* Topbar */
.bd-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0 4px;
}
.bd-user {
  display: flex; align-items: center; gap: 10px;
}
.bd-user-avatar {
  width: 32px; height: 32px;
  border-radius: 50%;
  background: rgba(10,132,255,0.2);
  border: 1px solid rgba(10,132,255,0.35);
  display: flex; align-items: center; justify-content: center;
  font-size: 15px; font-weight: 600; color: #0a84ff;
  flex-shrink: 0;
}
.bd-user-name { font-size: 15px; font-weight: 600; color: var(--text-primary); }

.bd-logout {
  background: none; border: none; cursor: pointer;
  color: var(--text-secondary); padding: 6px;
  border-radius: 8px; transition: color .15s, background .15s;
  display: flex; align-items: center;
}
.bd-logout:hover { color: #ff453a; background: rgba(255,69,58,0.1); }

/* Loading */
.bd-loading {
  display: flex; justify-content: center; padding: 40px;
}
.bd-spinner {
  width: 28px; height: 28px;
  border: 2.5px solid var(--bg-card);
  border-top-color: var(--accent-green);
  border-radius: 50%;
  animation: spin .8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Empty state */
.bd-empty {
  display: flex; flex-direction: column; align-items: center;
  gap: 10px; padding: 40px 20px; text-align: center;
}
.bd-empty-icon { font-size: 44px; }
.bd-empty-title { font-size: 17px; font-weight: 600; color: var(--text-primary); margin: 0; }
.bd-empty-sub   { font-size: 13px; color: var(--text-secondary); margin: 0; }

/* Period nav */
.bd-period-nav {
  display: flex; align-items: center; gap: 6px;
  padding: 8px 12px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 14px;
}
.bd-nav-btn {
  width: 30px; height: 30px; border-radius: 8px;
  background: var(--bg-input); border: 1px solid var(--border);
  color: var(--text-secondary); cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background .12s, color .12s;
  flex-shrink: 0;
}
.bd-nav-btn:disabled { opacity: 0.25; cursor: default; }
.bd-nav-btn:not(:disabled):hover { background: var(--border); color: #fff; }

.bd-period-label {
  flex: 1; text-align: center;
  font-size: 14px; font-weight: 600; color: var(--text-primary);
}
.bd-new-period-btn {
  font-size: 18px;
  color: var(--accent-green);
  background: rgba(48,209,88,0.1);
  border: 1px solid rgba(48,209,88,0.25);
  border-radius: 8px; padding: 4px 7px; cursor: pointer;
  transition: background .15s;
  flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
}
.bd-new-period-btn:hover { background: rgba(48,209,88,0.18); }

.bd-del-period-btn {
  font-size: 16px;
  color: var(--text-secondary);
  background: none;
  border: none;
  padding: 4px 2px;
  cursor: pointer;
  display: flex; align-items: center;
  transition: color .15s;
  flex-shrink: 0;
}
.bd-del-period-btn:hover { color: #ff453a; }

/* Hero card */
.bd-hero {
  display: flex; flex-direction: column; gap: 10px;
  text-align: center;
}
.bd-hero-label {
  font-size: 11px; font-weight: 600; text-transform: uppercase;
  letter-spacing: .8px; color: var(--text-secondary);
}
.bd-hero-total {
  font-size: 42px; font-weight: 900;
  color: var(--accent-green);
  font-variant-numeric: tabular-nums;
  letter-spacing: -1px;
  line-height: 1;
}
.bd-hero-meta {
  display: flex; flex-direction: column; gap: 6px;
  margin-top: 4px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}
.bd-hero-row { display: flex; align-items: center; justify-content: space-between; }
.bd-meta-key { font-size: 13px; color: var(--text-secondary); }
.bd-meta-val { font-size: 14px; font-weight: 700; color: var(--text-primary); font-variant-numeric: tabular-nums; }

/* Section header */
.bd-section-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 10px;
}
.bd-section-title { font-size: 13px; font-weight: 700; color: var(--text-secondary); text-transform: uppercase; letter-spacing: .4px; }
.bd-add-btn {
  display: flex; align-items: center; gap: 5px;
  font-size: 12px; font-weight: 600;
  color: var(--accent-green);
  background: rgba(48,209,88,0.1);
  border: 1px solid rgba(48,209,88,0.25);
  border-radius: 8px; padding: 4px 10px; cursor: pointer;
  transition: background .15s;
  font-family: inherit;
}
.bd-add-btn:hover { background: rgba(48,209,88,0.18); }

/* Account card */
.bd-account-card {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid var(--border);
  transition: opacity .12s;
}
.bd-account-card:last-child { border-bottom: none; padding-bottom: 0; }
.bd-account-card:first-of-type { padding-top: 0; }

.bd-acc-content {
  flex: 1; min-width: 0;
  display: flex; flex-direction: column; gap: 5px;
}

.bd-acc-main {
  display: flex; align-items: center; gap: 10px;
}
.bd-drag-handle {
  font-size: 18px; color: var(--text-secondary);
  cursor: grab; padding: 0 4px; flex-shrink: 0;
  touch-action: none;
  user-select: none;
}
.bd-drag-handle:active { cursor: grabbing; }
.bd-account-card.bd-dragging  { opacity: 0.4; }
.bd-account-card.bd-drag-over {
  border-top: 2px solid var(--accent-green);
  margin-top: -2px;
}
.bd-acc-icon { font-size: 18px; flex-shrink: 0; }
.bd-acc-name { flex: 1; font-size: 15px; font-weight: 600; color: var(--text-primary); }
.bd-transfer-btn {
  font-size: 16px; color: var(--text-secondary);
  background: var(--bg-input); border: 1px solid var(--border);
  border-radius: 8px; width: 30px; height: 30px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: background .12s, color .12s;
  flex-shrink: 0;
}
.bd-transfer-btn:hover { background: rgba(10,132,255,0.15); border-color: #0a84ff; color: #0a84ff; }

.bd-acc-balances {
  display: flex; align-items: center; gap: 6px;
  padding-left: 28px; /* align under name (icon 18px + gap 10px) */
  font-size: 13px;
  font-variant-numeric: tabular-nums;
}
.bd-bal-start   { color: var(--text-secondary); }
.bd-bal-arrow   { color: var(--border); }
.bd-bal-current { color: var(--text-primary); font-weight: 600; }
.bd-bal-delta   { font-weight: 700; }

/* Income / transfer rows */
.bd-list-row {
  display: flex; align-items: center; justify-content: space-between; gap: 10px;
  padding: 8px 0;
  border-bottom: 1px solid var(--border);
}
.bd-list-row:last-child { border-bottom: none; padding-bottom: 0; }
.bd-row-left { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.bd-row-date  { font-size: 11px; color: var(--text-secondary); }
.bd-row-label { font-size: 14px; color: var(--text-primary); font-weight: 500; }
.bd-row-note  { font-size: 12px; color: var(--text-secondary); }
.bd-advance-badge {
  font-size: 10px; font-weight: 600;
  color: #ff9f0a;
  background: rgba(255,159,10,0.12);
  border: 1px solid rgba(255,159,10,0.3);
  border-radius: 5px; padding: 1px 5px;
  margin-left: 5px; vertical-align: middle;
  white-space: nowrap;
}
.bd-row-right { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
.bd-row-amount { font-size: 15px; font-weight: 700; font-variant-numeric: tabular-nums; }
.bd-del-btn {
  background: none; border: none; cursor: pointer;
  font-size: 14px; opacity: 0.5;
  transition: opacity .15s;
  padding: 2px;
}
.bd-del-btn:hover { opacity: 1; }

/* Error */
.bd-error-bar {
  padding: 12px 16px;
  background: rgba(255,69,58,0.1);
  border: 1px solid var(--accent-red);
  border-radius: 12px;
  font-size: 13px; color: var(--accent-red);
  text-align: center;
}

/* Buttons */
.bd-btn-primary {
  width: 100%; padding: 15px;
  border-radius: 14px;
  background: var(--accent-green); color: #000;
  font-size: 16px; font-weight: 700;
  border: none; cursor: pointer;
  transition: opacity .15s, transform .1s;
}
.bd-btn-primary:active { transform: scale(0.98); }
.bd-btn-primary:disabled { opacity: 0.45; cursor: default; }

/* ── Shared sheet styles ─────────────────────────────────── */
.bd-sheet-backdrop {
  position: fixed; inset: 0; z-index: 300;
  background: rgba(0,0,0,0.6);
  display: flex; align-items: flex-end;
}
.bd-sheet {
  width: 100%;
  background: var(--bg-secondary);
  border-radius: 20px 20px 0 0;
  border-top: 1px solid var(--border);
  padding: 20px 20px calc(24px + env(safe-area-inset-bottom, 0px));
  animation: slideUp .25s ease;
  display: flex; flex-direction: column; gap: 16px;
  max-height: 85vh; overflow-y: auto;
}
@keyframes slideUp {
  from { transform: translateY(100%); }
  to   { transform: translateY(0); }
}
.bd-sheet-header {
  display: flex; align-items: center; justify-content: space-between;
}
.bd-sheet-title { font-size: 16px; font-weight: 700; color: var(--text-primary); }
.bd-sheet-close {
  width: 30px; height: 30px; border-radius: 50%;
  background: var(--bg-input); border: none;
  color: var(--text-secondary); cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background .15s;
}
.bd-sheet-close:hover { background: var(--border); color: #fff; }
.bd-sheet-info {
  font-size: 13px; color: var(--text-secondary);
  margin: -4px 0 0; line-height: 1.4;
}

/* Sheet fields */
.bd-field { display: flex; flex-direction: column; gap: 8px; }
.bd-label {
  font-size: 11px; font-weight: 600;
  color: var(--text-secondary); text-transform: uppercase; letter-spacing: .4px;
}
.bd-date-input, .bd-text-input {
  background: var(--bg-input); border: 1px solid var(--border);
  border-radius: 12px; padding: 13px 14px;
  font-size: 16px; color: var(--text-primary);
  font-family: inherit; outline: none;
  width: 100%; box-sizing: border-box;
}
.bd-input-wrap {
  display: flex; align-items: center; gap: 8px;
  background: var(--bg-input); border: 1px solid var(--border);
  border-radius: 12px; padding: 0 14px;
}
.bd-num-input {
  flex: 1; background: transparent; border: none; outline: none;
  font-size: 20px; font-weight: 600; color: var(--text-primary);
  font-family: inherit; padding: 14px 0;
  font-variant-numeric: tabular-nums;
  -moz-appearance: textfield;
}
.bd-num-input::-webkit-inner-spin-button,
.bd-num-input::-webkit-outer-spin-button { -webkit-appearance: none; }
.bd-currency { font-size: 18px; font-weight: 600; color: var(--text-secondary); }

/* Type grid */
.bd-type-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 8px;
}
.bd-type-btn {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 14px; border-radius: 10px;
  background: var(--bg-input); border: 1px solid var(--border);
  color: var(--text-secondary); font-size: 14px; font-weight: 500;
  cursor: pointer; transition: all .12s; font-family: inherit;
}
.bd-type-btn.active {
  background: rgba(10,132,255,0.15);
  border-color: #0a84ff; color: #fff;
}

/* Sheet error */
.bd-sheet-error {
  padding: 10px 14px;
  background: rgba(255,69,58,0.1);
  border: 1px solid var(--accent-red);
  border-radius: 10px;
  font-size: 13px; color: var(--accent-red);
  text-align: center;
}

/* Income categories */
.bd-cats {
  display: flex; flex-wrap: wrap; gap: 6px;
}
.bd-cat-btn {
  padding: 6px 12px; border-radius: 8px;
  background: var(--bg-input); border: 1px solid var(--border);
  color: var(--text-secondary); font-size: 13px; font-weight: 500;
  cursor: pointer; transition: all .12s; font-family: inherit;
}
.bd-cat-btn.active {
  background: rgba(48,209,88,0.15);
  border-color: var(--accent-green); color: #fff;
}
</style>
