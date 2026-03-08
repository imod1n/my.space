<template>
  <div class="card">
    <h2 class="chart-title">
      <span>📈</span> График расходов
    </h2>

    <!-- Переключатель режима -->
    <div class="mode-toggle">
      <button
        v-for="mode in modes"
        :key="mode.key"
        @click="activeMode = mode.key"
        class="mode-btn"
        :class="{ active: activeMode === mode.key }"
      >
        {{ mode.label }}
      </button>
    </div>

    <!-- Итого: 6 месяцев -->
    <div v-if="activeMode === 'total'">
      <div v-if="!hasTotalData" class="empty-chart">Недостаточно данных</div>
      <div v-else class="chart-wrap">
        <canvas ref="totalCanvas"></canvas>
      </div>
    </div>

    <!-- По категориям: текущий период -->
    <div v-if="activeMode === 'breakdown'">
      <div v-if="!hasCatData" class="empty-chart">Нет данных за выбранный период</div>
      <div v-else class="chart-wrap">
        <canvas ref="breakdownCanvas"></canvas>
      </div>
    </div>

    <!-- По годам: сравнение месяцев -->
    <div v-if="activeMode === 'trend'">
      <div v-if="!hasTrendData" class="empty-chart">Недостаточно данных</div>
      <div v-else class="trend-scroll">
        <div class="trend-inner">
          <canvas ref="trendCanvas"></canvas>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onUnmounted } from 'vue'
import {
  Chart,
  BarController, BarElement,
  LineController, LineElement, PointElement,
  CategoryScale, LinearScale,
  Tooltip, Legend,
} from 'chart.js'
import { usePaymentsStore, getCatMeta } from '../stores/payments'

Chart.register(
  BarController, BarElement,
  LineController, LineElement, PointElement,
  CategoryScale, LinearScale,
  Tooltip, Legend,
)

const props = defineProps({
  history: { type: Array, default: () => [] },
})

const store = usePaymentsStore()
const activeMode = ref('total')
const modes = [
  { key: 'total',     label: '📊 Итого' },
  { key: 'breakdown', label: '🗂️ По категориям' },
  { key: 'trend',     label: '📅 По годам' },
]

const totalCanvas     = ref(null)
const breakdownCanvas = ref(null)
const trendCanvas     = ref(null)
let totalChart     = null
let breakdownChart = null
let trendChart     = null

// ── Helpers ──────────────────────────────────────────────────
const MONTHS_SHORT = ['Янв','Фев','Мар','Апр','Май','Июн',
                      'Июл','Авг','Сен','Окт','Ноя','Дек']

function periodLabel(period) {
  if (!period) return ''
  const [y, m] = period.split('-')
  return MONTHS_SHORT[parseInt(m) - 1] + ' ' + y
}

const tooltipDefaults = {
  backgroundColor: '#2c2c2e',
  titleColor: '#8e8e93',
  bodyColor: '#fff',
  borderColor: '#38383a',
  borderWidth: 1,
  padding: 12,
  callbacks: {
    label: (ctx) => ` ${Math.round(ctx.parsed.y).toLocaleString('ru')} ₽`,
  },
}

const scalesDefaults = {
  x: {
    grid: { color: 'rgba(255,255,255,0.05)' },
    ticks: { color: '#8e8e93', font: { size: 11 } },
  },
  y: {
    grid: { color: 'rgba(255,255,255,0.05)' },
    ticks: {
      color: '#8e8e93',
      font: { size: 11 },
      callback: (v) => v >= 1000 ? (v / 1000).toFixed(0) + 'k' : v,
    },
    border: { dash: [4, 4] },
  },
}

// ── "Итого": история 6 месяцев (хронологически) ──────────────
const sortedHistory = computed(() =>
  [...props.history].sort((a, b) => a.period > b.period ? 1 : -1)
)
const hasTotalData = computed(() => sortedHistory.value.length >= 1)

function buildTotalChart() {
  if (!totalCanvas.value) return
  totalChart?.destroy(); totalChart = null

  const data   = sortedHistory.value.map(h => h.total)
  const labels = sortedHistory.value.map(h => periodLabel(h.period))
  const maxVal = Math.max(...data, 1)
  const last   = data.length - 1

  totalChart = new Chart(totalCanvas.value, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          type: 'bar',
          label: 'Итого',
          data,
          backgroundColor: data.map((v, i) =>
            i === last
              ? 'rgba(48,209,88,0.85)'
              : `rgba(10,132,255,${0.35 + 0.45 * (v / maxVal)})`
          ),
          borderRadius: 8,
          borderSkipped: false,
        },
        {
          type: 'line',
          label: 'Тренд',
          data,
          borderColor: 'rgba(48,209,88,0.55)',
          borderWidth: 2,
          pointRadius: 4,
          pointBackgroundColor: '#30d158',
          tension: 0.4,
          fill: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: tooltipDefaults },
      scales: scalesDefaults,
    },
  })
}

// ── "По годам": year-over-year grouped bars ──────────────────
const YEAR_COLORS = [
  { bg: 'rgba(10,132,255,0.8)',  border: '#0a84ff' },  // синий
  { bg: 'rgba(48,209,88,0.8)',   border: '#30d158' },  // зелёный
  { bg: 'rgba(255,159,10,0.8)',  border: '#ff9f0a' },  // оранжевый
  { bg: 'rgba(191,90,242,0.8)', border: '#bf5af2' },  // фиолетовый
]

const yearGroups = computed(() => {
  const map = {}
  for (const h of store.historyFull) {
    const [y, m] = h.period.split('-')
    if (!map[y]) map[y] = {}
    map[y][parseInt(m)] = h.total
  }
  return map
})
const hasTrendData = computed(() => Object.keys(yearGroups.value).length >= 1)

function buildTrendChart() {
  if (!trendCanvas.value) return
  trendChart?.destroy(); trendChart = null

  const years = Object.keys(yearGroups.value).sort()
  if (!years.length) return

  const datasets = years.map((year, i) => {
    const color = YEAR_COLORS[i % YEAR_COLORS.length]
    return {
      label: year,
      data: Array.from({ length: 12 }, (_, idx) => yearGroups.value[year][idx + 1] ?? null),
      backgroundColor: color.bg,
      borderColor: color.border,
      borderWidth: 0,
      borderRadius: 6,
      borderSkipped: false,
    }
  })

  trendChart = new Chart(trendCanvas.value, {
    type: 'bar',
    data: { labels: MONTHS_SHORT, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      onClick: (_event, elements) => {
        if (!elements.length) return
        const { datasetIndex, index } = elements[0]
        const year  = years[datasetIndex]
        const month = String(index + 1).padStart(2, '0')
        store.currentPeriod = `${year}-${month}`
        store.fetchStats()
      },
      onHover: (event, elements) => {
        event.native.target.style.cursor = elements.length ? 'pointer' : 'default'
      },
      plugins: {
        legend: {
          display: true,
          labels: { color: '#8e8e93', font: { size: 13 }, boxWidth: 14, borderRadius: 4 },
        },
        tooltip: tooltipDefaults,
      },
      scales: {
        x: {
          grid: { color: 'rgba(255,255,255,0.05)' },
          ticks: { color: '#8e8e93', font: { size: 12 } },
        },
        y: {
          grid: { color: 'rgba(255,255,255,0.05)' },
          ticks: {
            color: '#8e8e93',
            font: { size: 12 },
            callback: (v) => v >= 1000 ? (v / 1000).toFixed(0) + 'k' : v,
          },
          border: { dash: [4, 4] },
        },
      },
    },
  })
}

// ── "По категориям": текущий период ──────────────────────────
const catRows = computed(() => {
  const bc = store.stats?.by_category || {}
  return Object.entries(bc)
    .map(([name, amount]) => ({ name, amount, ...getCatMeta(name) }))
    .sort((a, b) => b.amount - a.amount)
})
const hasCatData = computed(() => catRows.value.length > 0)

function buildBreakdownChart() {
  if (!breakdownCanvas.value) return
  breakdownChart?.destroy(); breakdownChart = null

  const rows   = catRows.value
  const labels = rows.map(r => r.name)
  const data   = rows.map(r => r.amount)
  const colors = rows.map(r => r.color + 'cc')

  breakdownChart = new Chart(breakdownCanvas.value, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Сумма',
        data,
        backgroundColor: colors,
        borderRadius: 8,
        borderSkipped: false,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: tooltipDefaults },
      scales: scalesDefaults,
    },
  })
}

// ── Watchers ─────────────────────────────────────────────────
watch(
  () => props.history,
  async () => { await nextTick(); if (activeMode.value === 'total') buildTotalChart() },
  { deep: true, immediate: true }
)

watch(
  () => store.stats,
  async () => { await nextTick(); if (activeMode.value === 'breakdown') buildBreakdownChart() },
  { deep: true }
)

watch(
  () => store.historyFull,
  async () => { await nextTick(); if (activeMode.value === 'trend') buildTrendChart() },
  { deep: true }
)

watch(activeMode, async (mode) => {
  await nextTick()
  if (mode === 'total') buildTotalChart()
  else if (mode === 'breakdown') buildBreakdownChart()
  else buildTrendChart()
})

onUnmounted(() => {
  totalChart?.destroy()
  breakdownChart?.destroy()
  trendChart?.destroy()
})
</script>

<style scoped>
.chart-title {
  font-size: 15px; font-weight: 700;
  color: var(--text-primary);
  display: flex; align-items: center; gap: 8px;
  margin-bottom: 14px;
}

.mode-toggle {
  display: flex; gap: 4px;
  background: var(--bg-input);
  border-radius: 10px; padding: 4px;
  margin-bottom: 16px;
}
.mode-btn {
  flex: 1; padding: 8px 10px; border: none;
  background: transparent; color: var(--text-secondary);
  border-radius: 8px; font-size: 13px; font-weight: 600;
  cursor: pointer; transition: all .2s; font-family: inherit;
}
.mode-btn.active {
  background: var(--bg-card); color: var(--text-primary);
  box-shadow: 0 1px 4px rgba(0,0,0,.5);
}

.chart-wrap { position: relative; height: 200px; }
.chart-wrap--tall { height: 240px; }

.trend-scroll {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  /* тонкий скроллбар на десктопе */
  scrollbar-width: thin;
  scrollbar-color: var(--border) transparent;
}
.trend-scroll::-webkit-scrollbar { height: 4px; }
.trend-scroll::-webkit-scrollbar-track { background: transparent; }
.trend-scroll::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

.trend-inner {
  display: block;
  min-width: 1100px; /* мобиль скроллит, десктоп растягивается */
  position: relative;
  height: 300px;
}

.empty-chart {
  text-align: center; padding: 40px 0;
  font-size: 13px; color: var(--text-secondary);
}
</style>
