<template>
  <div class="pb-safe">

    <!-- Блокировка бюджета — поверх всего, как PinLock -->
    <BudgetLock v-if="activeTab === 'budget' && budgetLocked" @unlocked="budgetLocked = false" @back="activeTab = 'overview'" />

    <!-- Шапка -->
    <header class="sticky top-0 z-10 px-4 pb-3 flex items-center justify-between" style="background: rgba(17,17,17,0.9); backdrop-filter: blur(20px); border-bottom: 1px solid var(--border); padding-top: calc(env(safe-area-inset-top, 0px) + 12px)">
      <div class="flex items-center gap-3">
        <span class="text-2xl">🏠</span>
        <div>
          <h1 class="text-base font-bold text-white leading-tight">Сводная доска</h1>
        </div>
      </div>

      <!-- Переключатель месяца (скрыт на вкладке Бюджет) -->
      <div v-if="activeTab !== 'budget'" class="flex items-center gap-1 rounded-2xl px-1 py-1" style="background: var(--bg-card); border: 1px solid var(--border)">
        <button
          @click="store.changeMonth(-1)"
          class="w-8 h-8 rounded-xl flex items-center justify-center transition-all active:scale-90"
          style="color: var(--text-secondary)"
          onmouseover="this.style.background='var(--bg-input)'; this.style.color='#fff'"
          onmouseout="this.style.background='transparent'; this.style.color='var(--text-secondary)'"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M10 12L6 8L10 4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>

        <button
          @click="store.currentPeriod = store.todayPeriod(); store.fetchStats()"
          class="text-sm font-semibold px-3 transition-opacity active:opacity-60"
          style="color: #fff; min-width: 110px; text-align: center; letter-spacing: -0.2px; background: none; border: none; cursor: pointer; font-family: inherit"
          title="Вернуться к текущему месяцу"
        >
          {{ store.currentPeriodLabel }}
        </button>

        <button
          @click="store.changeMonth(1)"
          class="w-8 h-8 rounded-xl flex items-center justify-center transition-all active:scale-90"
          style="color: var(--text-secondary)"
          onmouseover="this.style.background='var(--bg-input)'; this.style.color='#fff'"
          onmouseout="this.style.background='transparent'; this.style.color='var(--text-secondary)'"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M6 4L10 8L6 12" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </header>

    <!-- Контент -->
    <main class="px-4 pt-4 space-y-4 pb-8">

      <!-- ГЕРОЙ: итоговая сумма (скрыт на вкладке Бюджет) -->
      <div v-if="activeTab !== 'budget'" class="card fade-in text-center py-6" style="position: relative">
        <!-- Кнопка калькулятора -->
        <button @click="openCalc" class="calc-icon-btn" title="Калькулятор периодов">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <rect x="4" y="2" width="16" height="20" rx="2"/>
            <line x1="8" y1="6" x2="16" y2="6"/>
            <line x1="8" y1="10" x2="10" y2="10"/>
            <line x1="14" y1="10" x2="16" y2="10"/>
            <line x1="8" y1="14" x2="10" y2="14"/>
            <line x1="14" y1="14" x2="16" y2="14"/>
            <line x1="8" y1="18" x2="10" y2="18"/>
            <line x1="14" y1="18" x2="16" y2="18"/>
          </svg>
        </button>

        <div class="text-xs font-medium uppercase tracking-widest mb-2" style="color: var(--text-secondary)">
          ИТОГО {{ store.currentPeriodLabel.toUpperCase() }}
        </div>

        <div v-if="store.loading" class="flex items-center justify-center gap-2 py-4">
          <div class="w-6 h-6 border-2 rounded-full animate-spin" style="border-color: var(--accent-green); border-top-color: transparent"></div>
        </div>

        <div v-else>
          <div class="text-5xl font-black tracking-tight mb-2" style="color: var(--accent-green); font-variant-numeric: tabular-nums">
            {{ formatRub(store.stats?.total ?? 0) }}
          </div>
        </div>
      </div>

      <!-- Переключатель месяца скрыт на вкладке Бюджет -->

      <!-- Вкладки -->
      <div class="flex rounded-ios-sm overflow-hidden" style="background: var(--bg-card); border: 1px solid var(--border)">
        <!-- Обзор доски -->
        <button
          @click="activeTab = 'overview'"
          class="flex-1 py-2.5 text-sm font-semibold transition-all"
          :style="activeTab === 'overview' ? 'background: var(--bg-input); color: #fff' : 'color: var(--text-secondary)'"
        >
          <span class="sm:hidden text-lg leading-none">📊</span>
          <span class="hidden sm:inline">📊 Обзор доски</span>
        </button>
        <!-- Добавить платёж -->
        <button
          @click="activeTab = 'add'"
          class="flex-1 py-2.5 text-sm font-semibold transition-all"
          :style="activeTab === 'add' ? 'background: var(--bg-input); color: #fff' : 'color: var(--text-secondary)'"
        >
          <span class="sm:hidden text-lg leading-none">➕</span>
          <span class="hidden sm:inline">➕ Добавить платеж</span>
        </button>
        <!-- Данные — только на десктопе -->
        <button
          @click="activeTab = 'data'"
          class="hidden sm:block flex-1 py-2.5 text-sm font-semibold transition-all"
          :style="activeTab === 'data' ? 'background: var(--bg-input); color: #fff' : 'color: var(--text-secondary)'"
        >
          📤 Данные
        </button>
        <!-- Бюджет -->
        <button
          @click="activeTab = 'budget'"
          class="flex-1 py-2.5 text-sm font-semibold transition-all"
          :style="activeTab === 'budget' ? 'background: var(--bg-input); color: #fff' : 'color: var(--text-secondary)'"
        >
          <span class="sm:hidden text-lg leading-none">💰</span>
          <span class="hidden sm:inline">💰 Бюджет</span>
        </button>
      </div>

      <!-- Вкладка: Обзор -->
      <template v-if="activeTab === 'overview'">
        <StatsTable />
        <MonthlyChart :history="store.history" />
      </template>

      <!-- Вкладка: Добавить -->
      <template v-if="activeTab === 'add'">
        <PaymentForm @added="onPaymentAdded" />
      </template>

      <!-- Вкладка: Данные -->
      <template v-if="activeTab === 'data'">
        <ImportExport />
      </template>

      <!-- Вкладка: Бюджет -->
      <template v-if="activeTab === 'budget'">
        <BudgetDashboard v-if="!budgetLocked" />
      </template>

      <!-- Ошибка -->
      <div v-if="store.error" class="card text-center" style="background: rgba(255,69,58,0.1); border-color: var(--accent-red)">
        <p class="text-sm" style="color: var(--accent-red)">{{ store.error }}</p>
        <button @click="store.fetchStats()" class="mt-2 text-xs underline" style="color: var(--accent-blue)">Повторить</button>
      </div>

    </main>

    <!-- ── Калькулятор периодов ── -->
    <Teleport to="body">
      <div v-if="showCalc" class="calc-backdrop" @click.self="showCalc = false">
        <div class="calc-sheet">

          <!-- Заголовок -->
          <div class="calc-header">
            <span class="calc-title">Калькулятор периодов</span>
            <button class="calc-close" @click="showCalc = false">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>

          <!-- Селекторы периода -->
          <div class="calc-row">
            <!-- Пикер "С" -->
            <div class="calc-field">
              <label class="calc-label">С</label>
              <div class="calc-picker">
                <div class="calc-year-nav">
                  <button class="calc-year-btn" :disabled="calcFromPickerYear <= minAvailYear" @click="calcFromPickerYear--">
                    <svg width="12" height="12" viewBox="0 0 16 16" fill="none"><path d="M10 12L6 8L10 4" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
                  </button>
                  <span class="calc-year-label">{{ calcFromPickerYear }}</span>
                  <button class="calc-year-btn" :disabled="calcFromPickerYear >= maxAvailYear" @click="calcFromPickerYear++">
                    <svg width="12" height="12" viewBox="0 0 16 16" fill="none"><path d="M6 4L10 8L6 12" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
                  </button>
                </div>
                <div class="calc-month-grid">
                  <button
                    v-for="(mname, mi) in MONTHS_SHORT" :key="mi"
                    class="calc-month-btn"
                    :disabled="isFromMonthDisabled(calcFromPickerYear, mi + 1)"
                    :class="{ active: isFromMonthActive(calcFromPickerYear, mi + 1) }"
                    @click="selectFrom(calcFromPickerYear, mi + 1)"
                  >{{ mname }}</button>
                </div>
              </div>
            </div>
            <div class="calc-sep">—</div>
            <!-- Пикер "По" -->
            <div class="calc-field">
              <label class="calc-label">По</label>
              <div class="calc-picker">
                <div class="calc-year-nav">
                  <button class="calc-year-btn" :disabled="calcToPickerYear <= minAvailYear" @click="calcToPickerYear--">
                    <svg width="12" height="12" viewBox="0 0 16 16" fill="none"><path d="M10 12L6 8L10 4" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
                  </button>
                  <span class="calc-year-label">{{ calcToPickerYear }}</span>
                  <button class="calc-year-btn" :disabled="calcToPickerYear >= maxAvailYear" @click="calcToPickerYear++">
                    <svg width="12" height="12" viewBox="0 0 16 16" fill="none"><path d="M6 4L10 8L6 12" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
                  </button>
                </div>
                <div class="calc-month-grid">
                  <button
                    v-for="(mname, mi) in MONTHS_SHORT" :key="mi"
                    class="calc-month-btn"
                    :disabled="isToMonthDisabled(calcToPickerYear, mi + 1)"
                    :class="{ active: isToMonthActive(calcToPickerYear, mi + 1) }"
                    @click="selectTo(calcToPickerYear, mi + 1)"
                  >{{ mname }}</button>
                </div>
              </div>
            </div>
          </div>

          <!-- Результат -->
          <div class="calc-result">
            <div class="calc-result-meta">
              {{ calcMonthsCount }} {{ monthsWord(calcMonthsCount) }}
              <span v-if="calcMonthsCount !== calcMonthsWithData"> · данных за {{ calcMonthsWithData }}</span>
            </div>
            <div class="calc-result-sum">{{ formatRub(calcTotal) }}</div>
            <div v-if="calcMonthsWithData > 0" class="calc-result-avg">
              среднее {{ formatRub(Math.round(calcTotal / calcMonthsWithData)) }} / мес
            </div>

            <!-- Детализация по объектам -->
            <div v-if="calcByObject.length > 0" class="calc-objects">
              <div v-for="obj in calcByObject" :key="obj.name" class="calc-obj-group">
                <div class="calc-obj-row" @click="toggleObject(obj.name)">
                  <span class="calc-obj-icon">{{ obj.icon }}</span>
                  <span class="calc-obj-name">{{ obj.name }}</span>
                  <span class="calc-obj-sum">{{ formatRub(obj.total) }}</span>
                  <span class="calc-obj-chevron" :class="{ expanded: expandedObjects.has(obj.name) }">
                    <svg width="12" height="12" viewBox="0 0 16 16" fill="none">
                      <path d="M4 6L8 10L12 6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                  </span>
                </div>
                <div v-if="expandedObjects.has(obj.name)" class="calc-cats">
                  <div v-for="cat in obj.categories" :key="cat.name" class="calc-cat-row">
                    <span class="calc-cat-dot" :style="{ background: cat.color }"></span>
                    <span class="calc-cat-name">{{ cat.name }}</span>
                    <span class="calc-cat-sum">{{ formatRub(cat.total) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { usePaymentsStore } from '../stores/payments'
import PaymentForm from '../components/PaymentForm.vue'
import StatsTable from '../components/StatsTable.vue'
import MonthlyChart from '../components/MonthlyChart.vue'
import ImportExport from '../components/ImportExport.vue'
// ── Бюджет: изолированный раздел ──────────────────────────────────────────
import BudgetLock from '../components/BudgetLock.vue'
import BudgetDashboard from '../components/BudgetDashboard.vue'
import { useBudgetStore } from '../stores/budget'

const store = usePaymentsStore()
const budgetStore = useBudgetStore()
const activeTab = ref('overview')

// Перепоказывать BudgetLock при возврате из фона > 30 мин или после logout
const budgetLocked = ref(!budgetStore.isAuthenticated)
watch(() => budgetStore.isAuthenticated, (val) => { if (!val) budgetLocked.value = true })
let budgetHiddenAt = 0
function onBudgetVisibilityChange() {
  if (document.hidden) {
    budgetHiddenAt = Date.now()
  } else if (activeTab.value === 'budget' && budgetStore.isAuthenticated) {
    if (Date.now() - budgetHiddenAt > 30 * 60 * 1000) {
      budgetLocked.value = true
    }
  }
}
document.addEventListener('visibilitychange', onBudgetVisibilityChange)
onUnmounted(() => {
  document.removeEventListener('visibilitychange', onBudgetVisibilityChange)
})

const tabs = [
  { key: 'overview', label: '📊 Обзор доски' },
  { key: 'add',      label: '➕ Добавить платеж' },
  { key: 'data',     label: '📤 Данные' },
]

function formatRub(n) {
  return Number(n).toLocaleString('ru-RU') + ' ₽'
}

function onPaymentAdded() {
  activeTab.value = 'overview'
}

onMounted(() => store.init())

// ── Калькулятор ────────────────────────────────────────────
const showCalc       = ref(false)
const calcFrom       = ref('')
const calcTo         = ref('')
const calcFromPickerYear = ref(new Date().getFullYear())
const calcToPickerYear   = ref(new Date().getFullYear())

const MONTHS_SHORT = ['Янв','Фев','Мар','Апр','Май','Июн','Июл','Авг','Сен','Окт','Ноя','Дек']
const MONTHS_FULL  = ['Январь','Февраль','Март','Апрель','Май','Июнь',
                      'Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь']

const availablePeriods = computed(() => {
  const sorted = [...store.historyFull]
    .sort((a, b) => a.period > b.period ? 1 : -1)
  return sorted.map(h => {
    const [y, m] = h.period.split('-')
    return { value: h.period, label: MONTHS_FULL[parseInt(m) - 1] + ' ' + y }
  })
})

const availablePeriodsSet = computed(() => new Set(availablePeriods.value.map(p => p.value)))

const minAvailYear = computed(() =>
  availablePeriods.value.length ? parseInt(availablePeriods.value[0].value) : new Date().getFullYear()
)
const maxAvailYear = computed(() =>
  availablePeriods.value.length ? parseInt(availablePeriods.value.at(-1).value) : new Date().getFullYear()
)

function pStr(year, month) {
  return `${year}-${String(month).padStart(2, '0')}`
}

function isFromMonthDisabled(year, month) {
  const p = pStr(year, month)
  return !availablePeriodsSet.value.has(p) || p > calcTo.value
}
function isToMonthDisabled(year, month) {
  const p = pStr(year, month)
  return !availablePeriodsSet.value.has(p) || p < calcFrom.value
}
function isFromMonthActive(year, month) { return pStr(year, month) === calcFrom.value }
function isToMonthActive(year, month)   { return pStr(year, month) === calcTo.value   }

function selectFrom(year, month) {
  const p = pStr(year, month)
  if (!availablePeriodsSet.value.has(p) || p > calcTo.value) return
  calcFrom.value = p
}
function selectTo(year, month) {
  const p = pStr(year, month)
  if (!availablePeriodsSet.value.has(p) || p < calcFrom.value) return
  calcTo.value = p
}

function openCalc() {
  const periods = availablePeriods.value
  const d = new Date()
  const todayStr = pStr(d.getFullYear(), d.getMonth() + 1)
  const d3ago = (() => { const x = new Date(); x.setMonth(x.getMonth() - 3); return pStr(x.getFullYear(), x.getMonth() + 1) })()
  const lastPeriod  = periods.findLast(p => p.value <= todayStr)?.value  ?? periods.at(-1)?.value ?? todayStr
  const firstPeriod = periods.find(p => p.value >= d3ago)?.value ?? periods[0]?.value ?? d3ago
  calcTo.value   = lastPeriod
  calcFrom.value = firstPeriod <= lastPeriod ? firstPeriod : lastPeriod
  calcToPickerYear.value   = parseInt(calcTo.value)
  calcFromPickerYear.value = parseInt(calcFrom.value)
  showCalc.value = true
}

// Все периоды в диапазоне [calcFrom, calcTo]
const periodsInRange = computed(() =>
  store.historyFull.filter(h => h.period >= calcFrom.value && h.period <= calcTo.value)
)

const calcTotal = computed(() =>
  periodsInRange.value.reduce((sum, h) => sum + h.total, 0)
)

const calcMonthsWithData = computed(() => periodsInRange.value.length)

// Сколько календарных месяцев в диапазоне (включительно)
const calcMonthsCount = computed(() => {
  if (!calcFrom.value || !calcTo.value || calcFrom.value > calcTo.value) return 0
  const [fy, fm] = calcFrom.value.split('-').map(Number)
  const [ty, tm] = calcTo.value.split('-').map(Number)
  return (ty - fy) * 12 + (tm - fm) + 1
})

const OBJECTS = [
  { name: 'Квартира 1',    icon: '🏠' },
  { name: 'Квартира 2',    icon: '🏢' },
  { name: 'Загородный дом', icon: '🏡' },
  { name: 'Пляжный домик', icon: '🏖️' },
]

const CATEGORIES = [
  { name: 'Коммунальные',  color: '#0a84ff' },
  { name: 'Электричество', color: '#ffd60a' },
  { name: 'Интернет',      color: '#bf5af2' },
  { name: 'Телевидение',   color: '#30d158' },
  { name: 'Мусор',         color: '#636366' },
  { name: 'Членские',      color: '#ff9f0a' },
  { name: 'Уборка снега',  color: '#5ac8fa' },
  { name: 'Прочее',        color: '#8e8e93' },
]

const expandedObjects = ref(new Set())

function toggleObject(name) {
  const s = new Set(expandedObjects.value)
  s.has(name) ? s.delete(name) : s.add(name)
  expandedObjects.value = s
}

// Детализация по объектам + категориям из store.payments
const calcByObject = computed(() => {
  const inRange = store.payments.filter(p =>
    p.period >= calcFrom.value && p.period <= calcTo.value
  )
  const data = {}
  for (const p of inRange) {
    const name = p.object_name || 'Без объекта'
    const cat  = p.category   || 'Прочее'
    if (!data[name]) data[name] = { total: 0, cats: {} }
    data[name].total += p.amount
    data[name].cats[cat] = (data[name].cats[cat] || 0) + p.amount
  }
  return Object.entries(data)
    .map(([name, { total, cats }]) => ({
      name,
      total,
      icon: OBJECTS.find(o => o.name === name)?.icon || '🏠',
      categories: Object.entries(cats)
        .map(([cname, ctotal]) => ({
          name:  cname,
          total: ctotal,
          color: CATEGORIES.find(c => c.name === cname)?.color || '#8e8e93',
        }))
        .sort((a, b) => b.total - a.total),
    }))
    .sort((a, b) => b.total - a.total)
})

function monthsWord(n) {
  if (n % 100 >= 11 && n % 100 <= 19) return 'месяцев'
  const r = n % 10
  if (r === 1) return 'месяц'
  if (r >= 2 && r <= 4) return 'месяца'
  return 'месяцев'
}
</script>

<style>
.pb-safe {
  padding-bottom: env(safe-area-inset-bottom, 0px);
}
</style>

<style scoped>
/* Кнопка калькулятора в герое */
.calc-icon-btn {
  position: absolute;
  top: 12px; right: 12px;
  width: 34px; height: 34px;
  border-radius: 10px;
  border: none;
  background: var(--bg-input);
  color: var(--text-secondary);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  transition: background .15s, color .15s;
}
.calc-icon-btn:hover { background: var(--border); color: #fff; }

/* Backdrop */
.calc-backdrop {
  position: fixed; inset: 0; z-index: 100;
  background: rgba(0,0,0,0.6);
  display: flex; align-items: flex-end;
}

/* Bottom sheet */
.calc-sheet {
  width: 100%;
  background: var(--bg-secondary);
  border-radius: 20px 20px 0 0;
  border-top: 1px solid var(--border);
  padding: 20px 20px calc(20px + env(safe-area-inset-bottom, 0px));
  animation: slideUp .25s ease;
}
@keyframes slideUp {
  from { transform: translateY(100%); }
  to   { transform: translateY(0); }
}

.calc-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 20px;
}
.calc-title {
  font-size: 16px; font-weight: 700; color: var(--text-primary);
}
.calc-close {
  width: 30px; height: 30px; border-radius: 50%;
  background: var(--bg-input); border: none;
  color: var(--text-secondary); cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background .15s;
}
.calc-close:hover { background: var(--border); color: #fff; }

/* Строка с селекторами */
.calc-row {
  display: flex; align-items: center; gap: 10px;
  margin-bottom: 24px;
}
.calc-field { flex: 1; display: flex; flex-direction: column; gap: 6px; }
.calc-label { font-size: 11px; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; letter-spacing: .5px; text-align: center; }

/* Пикер год + сетка месяцев */
.calc-picker {
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
}
.calc-year-nav {
  display: flex; align-items: center; justify-content: space-between;
  padding: 5px 4px;
  border-bottom: 1px solid var(--border);
}
.calc-year-btn {
  width: 26px; height: 26px; flex-shrink: 0;
  border: none; background: transparent;
  color: var(--text-secondary); cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  border-radius: 6px; transition: background .15s, color .15s;
}
.calc-year-btn:hover:not(:disabled) { background: var(--border); color: #fff; }
.calc-year-btn:disabled { opacity: 0.25; cursor: default; }
.calc-year-label {
  font-size: 14px; font-weight: 700; color: var(--text-primary);
}
.calc-month-grid {
  display: grid; grid-template-columns: repeat(3, 1fr);
  gap: 2px; padding: 4px;
}
.calc-month-btn {
  padding: 7px 2px;
  border: none; background: transparent;
  color: var(--text-secondary);
  font-size: 12px; font-weight: 500;
  border-radius: 6px; cursor: pointer;
  transition: background .15s, color .15s;
  font-family: inherit;
}
.calc-month-btn:hover:not(:disabled):not(.active) { background: var(--border); color: #fff; }
.calc-month-btn:disabled { opacity: 0.2; cursor: default; }
.calc-month-btn.active {
  background: var(--accent-green); color: #000;
  font-weight: 700;
}

.calc-sep {
  font-size: 18px; color: var(--text-secondary);
  padding-top: 22px;
}

/* Результат */
.calc-result {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 18px;
  text-align: center;
}
.calc-result-meta {
  font-size: 12px; color: var(--text-secondary);
  margin-bottom: 8px;
}
.calc-result-sum {
  font-size: 36px; font-weight: 900;
  color: var(--accent-green);
  font-variant-numeric: tabular-nums;
  letter-spacing: -1px;
}
.calc-result-avg {
  font-size: 13px; color: var(--text-secondary);
  margin-top: 6px;
}

/* Детализация по объектам */
.calc-objects {
  margin-top: 16px;
  border-top: 1px solid var(--border);
  padding-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.calc-obj-group {
  display: flex;
  flex-direction: column;
}
.calc-obj-row {
  display: flex;
  align-items: center;
  gap: 10px;
  text-align: left;
}
.calc-obj-icon {
  font-size: 16px;
  flex-shrink: 0;
}
.calc-obj-name {
  flex: 1;
  font-size: 14px;
  color: var(--text-secondary);
}
.calc-obj-sum {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
}
.calc-obj-chevron {
  color: var(--text-secondary);
  transition: transform .2s;
  flex-shrink: 0;
}
.calc-obj-chevron.expanded {
  transform: rotate(180deg);
}
.calc-obj-row {
  cursor: pointer;
}
.calc-obj-row:hover .calc-obj-name {
  color: var(--text-primary);
}

/* Категории под объектом */
.calc-cats {
  display: flex;
  flex-direction: column;
  gap: 5px;
  padding: 4px 0 4px 26px;
}
.calc-cat-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.calc-cat-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}
.calc-cat-name {
  flex: 1;
  font-size: 12px;
  color: var(--text-secondary);
}
.calc-cat-sum {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
}
</style>
