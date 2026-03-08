<template>
  <div class="pb-safe">

    <!-- Шапка -->
    <header class="sticky top-0 z-10 px-4 pb-3 flex items-center justify-between" style="background: rgba(17,17,17,0.9); backdrop-filter: blur(20px); border-bottom: 1px solid var(--border); padding-top: calc(env(safe-area-inset-top, 0px) + 12px)">
      <div class="flex items-center gap-3">
        <span class="text-2xl">🏠</span>
        <div>
          <h1 class="text-base font-bold text-white leading-tight">Сводная доска</h1>
        </div>
      </div>

      <!-- Переключатель месяца -->
      <div class="flex items-center gap-1 rounded-2xl px-1 py-1" style="background: var(--bg-card); border: 1px solid var(--border)">
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

      <!-- ГЕРОЙ: итоговая сумма -->
      <div class="card fade-in text-center py-6" style="position: relative">
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

      <!-- Вкладки -->
      <div class="flex rounded-ios-sm overflow-hidden" style="background: var(--bg-card); border: 1px solid var(--border)">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="activeTab = tab.key"
          class="flex-1 py-2.5 text-sm font-semibold transition-all"
          :style="activeTab === tab.key
            ? 'background: var(--bg-input); color: #fff'
            : 'color: var(--text-secondary)'"
        >
          {{ tab.label }}
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
            <div class="calc-field">
              <label class="calc-label">С</label>
              <select v-model="calcFrom" class="calc-select">
                <option v-for="p in availablePeriods" :key="p.value" :value="p.value">
                  {{ p.label }}
                </option>
              </select>
            </div>
            <div class="calc-sep">—</div>
            <div class="calc-field">
              <label class="calc-label">По</label>
              <select v-model="calcTo" class="calc-select">
                <option v-for="p in availablePeriods" :key="p.value" :value="p.value">
                  {{ p.label }}
                </option>
              </select>
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
              <div
                v-for="obj in calcByObject"
                :key="obj.name"
                class="calc-obj-row"
              >
                <span class="calc-obj-icon">{{ obj.icon }}</span>
                <span class="calc-obj-name">{{ obj.name }}</span>
                <span class="calc-obj-sum">{{ formatRub(obj.total) }}</span>
              </div>
            </div>
          </div>

        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { usePaymentsStore } from '../stores/payments'
import PaymentForm from '../components/PaymentForm.vue'
import StatsTable from '../components/StatsTable.vue'
import MonthlyChart from '../components/MonthlyChart.vue'
import ImportExport from '../components/ImportExport.vue'

const store = usePaymentsStore()
const activeTab = ref('overview')

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
const showCalc = ref(false)
const calcFrom = ref('')
const calcTo   = ref('')

const MONTHS_FULL = ['Январь','Февраль','Март','Апрель','Май','Июнь',
                     'Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь']

const availablePeriods = computed(() => {
  const sorted = [...store.historyFull]
    .sort((a, b) => a.period > b.period ? 1 : -1)
  return sorted.map(h => {
    const [y, m] = h.period.split('-')
    return { value: h.period, label: MONTHS_FULL[parseInt(m) - 1] + ' ' + y }
  })
})

function openCalc() {
  const d = new Date()
  calcTo.value = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
  d.setMonth(d.getMonth() - 3)
  calcFrom.value = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
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

// Детализация по объектам из store.payments
const calcByObject = computed(() => {
  const inRange = store.payments.filter(p =>
    p.period >= calcFrom.value && p.period <= calcTo.value
  )
  const totals = {}
  for (const p of inRange) {
    const name = p.object_name || 'Без объекта'
    totals[name] = (totals[name] || 0) + p.amount
  }
  const OBJECTS = [
    { name: 'Квартира 1',    icon: '🏠' },
    { name: 'Квартира 2',    icon: '🏢' },
    { name: 'Загородный дом', icon: '🏡' },
    { name: 'Пляжный домик', icon: '🏖️' },
  ]
  return Object.entries(totals)
    .map(([name, total]) => ({
      name,
      total,
      icon: OBJECTS.find(o => o.name === name)?.icon || '🏠',
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
.calc-label { font-size: 11px; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; letter-spacing: .5px; }
.calc-select {
  width: 100%; padding: 10px 12px;
  background: var(--bg-input); border: 1px solid var(--border);
  border-radius: 10px; color: var(--text-primary);
  font-size: 15px; font-family: inherit;
  appearance: none; cursor: pointer;
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
</style>
