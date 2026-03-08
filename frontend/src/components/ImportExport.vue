<template>
  <div class="ie-root">

    <!-- EXPORT -->
    <div class="ie-card">
      <div class="ie-title">Экспорт данных</div>
      <p class="ie-hint">Скачать все платежи в CSV — открывается в Excel и Google Таблицах</p>
      <button class="ie-btn ie-btn--green" @click="exportCSV" :disabled="!store.payments.length">
        Скачать CSV · {{ store.payments.length }} записей
      </button>
    </div>

    <!-- IMPORT -->
    <div class="ie-card">
      <div class="ie-title">Импорт данных</div>
      <p class="ie-hint">
        Загрузите CSV того же формата что при экспорте.<br>
        Колонки: <code>category, object_name, amount, date, period, note</code>
      </p>

      <!-- File picker -->
      <label class="ie-dropzone">
        <input type="file" accept=".csv,text/csv" @change="onFile" />
        <div class="ie-dropzone-inner" :class="{ 'has-file': fileName }">
          <div v-if="!fileName">
            <div class="ie-dropzone-icon">📁</div>
            Нажмите для выбора CSV
          </div>
          <div v-else>📄 {{ fileName }}</div>
        </div>
      </label>

      <!-- Parse error -->
      <div v-if="parseError" class="ie-parse-error">{{ parseError }}</div>

      <!-- Preview -->
      <template v-if="parsedRows.length">
        <div class="ie-table-wrap">
          <table class="ie-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Категория</th>
                <th>Объект</th>
                <th>Сумма</th>
                <th>Дата</th>
                <th>Период</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(row, i) in parsedRows"
                :key="i"
                :class="row._errors.length ? 'tr--err' : row._duplicate ? 'tr--dup' : 'tr--ok'"
              >
                <td class="td-num">{{ i + 1 }}</td>
                <td>{{ row.category }}</td>
                <td>{{ row.object_name }}</td>
                <td>{{ row.amount }}</td>
                <td>{{ row.date }}</td>
                <td>{{ row.period }}</td>
                <td>
                  <span
                    v-if="row._errors.length"
                    class="ie-badge ie-badge--err"
                    :title="row._errors.join('\n')"
                  >✗</span>
                  <span
                    v-else-if="row._duplicate"
                    class="ie-badge ie-badge--dup"
                    title="Уже есть в базе — пропустим"
                  >≡</span>
                  <span v-else class="ie-badge ie-badge--ok">✓</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="ie-stats">
          <span class="ie-stat-ok">✓ {{ validRows.length }} готово</span>
          <span v-if="dupRows.length" class="ie-stat-dup">≡ {{ dupRows.length }} дубликатов</span>
          <span v-if="invalidRows.length" class="ie-stat-err">✗ {{ invalidRows.length }} ошибок</span>
        </div>

        <!-- Progress -->
        <div v-if="importing" class="ie-progress-wrap">
          <div class="ie-progress-track">
            <div class="ie-progress-fill" :style="{ width: progressPct + '%' }"></div>
          </div>
          <div class="ie-progress-txt">{{ importedCount }} / {{ validRows.length }}</div>
        </div>

        <!-- Result -->
        <template v-if="importDone">
          <div class="ie-done">Импортировано {{ importedCount }} из {{ validRows.length }}</div>
          <div v-if="importSkipped" class="ie-skip">Пропущено дубликатов: {{ importSkipped }}</div>
          <div v-if="importFailed" class="ie-fail">Ошибок при загрузке: {{ importFailed }}</div>
        </template>

        <button
          class="ie-btn ie-btn--blue"
          :disabled="!validRows.length || importing"
          @click="doImport"
        >
          <span v-if="importing">Импортируем…</span>
          <span v-else>Импортировать {{ validRows.length }} строк</span>
        </button>
      </template>
    </div>

    <!-- CLEAR DB -->
    <div class="ie-card ie-card--danger">
      <div class="ie-title">Очистить базу данных</div>
      <p class="ie-hint">Удалить все платежи без возможности восстановления. Сделайте экспорт перед очисткой.</p>

      <template v-if="clearStep === 0">
        <button class="ie-btn ie-btn--red" @click="clearStep = 1">Очистить базу</button>
      </template>

      <template v-else-if="clearStep === 1">
        <p class="ie-confirm-txt">Вы уверены? Все данные будут удалены.</p>
        <div class="ie-confirm-btns">
          <button class="ie-btn ie-btn--ghost" @click="clearStep = 0">Отмена</button>
          <button class="ie-btn ie-btn--red" @click="clearStep = 2">Да, удалить</button>
        </div>
      </template>

      <template v-else>
        <p class="ie-confirm-txt ie-confirm-txt--warn">Последнее предупреждение! Отменить невозможно.</p>
        <div class="ie-confirm-btns">
          <button class="ie-btn ie-btn--ghost" @click="clearStep = 0">Отмена</button>
          <button class="ie-btn ie-btn--red" :disabled="clearLoading" @click="doClear">
            <span v-if="clearLoading">Удаляем…</span>
            <span v-else>Удалить всё</span>
          </button>
        </div>
      </template>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { usePaymentsStore, CATEGORIES, OBJECTS } from '../stores/payments'
import * as api from '../api/payments'

const store = usePaymentsStore()

onMounted(() => store.fetchPayments())

const fileName      = ref('')
const parseError    = ref('')
const parsedRows    = ref([])
const importing     = ref(false)
const importedCount = ref(0)
const importFailed  = ref(0)
const importSkipped = ref(0)
const importDone    = ref(false)

// ── Clear DB ────────────────────────────────────────────────────
const clearStep    = ref(0)   // 0=hidden 1=first confirm 2=second confirm
const clearLoading = ref(false)

async function doClear() {
  clearLoading.value = true
  try {
    await api.deleteAllPayments()
    await store.fetchStats()
    await store.fetchPayments()
    clearStep.value = 0
  } finally {
    clearLoading.value = false
  }
}

const VALID_CATS = CATEGORIES.map(c => c.name)
const VALID_OBJS = OBJECTS.map(o => o.name)

// ── CSV Export ──────────────────────────────────────────────────
function exportCSV() {
  const headers = ['category', 'object_name', 'amount', 'date', 'period', 'note']
  const rows = store.payments.map(p =>
    headers.map(h => `"${String(p[h] ?? '').replace(/"/g, '""')}"`).join(',')
  )
  const csv = '\ufeff' + [headers.join(','), ...rows].join('\r\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `kommunalka_${new Date().toISOString().slice(0, 10)}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

// ── CSV Parsing ─────────────────────────────────────────────────
function parseCSVLine(line) {
  const result = []
  let cur = '', inQ = false
  for (let i = 0; i < line.length; i++) {
    const c = line[i]
    if (c === '"') {
      if (inQ && line[i + 1] === '"') { cur += '"'; i++ }
      else inQ = !inQ
    } else if (c === ',' && !inQ) {
      result.push(cur); cur = ''
    } else {
      cur += c
    }
  }
  result.push(cur)
  return result
}

function validateRow(row) {
  const errors = []
  if (!VALID_CATS.includes(row.category))
    errors.push(`Категория "${row.category}" не найдена`)
  if (!VALID_OBJS.includes(row.object_name))
    errors.push(`Объект "${row.object_name}" не найден`)
  if (!row.amount || isNaN(Number(row.amount)) || Number(row.amount) <= 0)
    errors.push('Сумма должна быть > 0')
  if (!/^\d{4}-\d{2}-\d{2}$/.test(row.date))
    errors.push('Дата: формат YYYY-MM-DD')
  if (!/^\d{4}-\d{2}$/.test(row.period))
    errors.push('Период: формат YYYY-MM')
  return errors
}

function onFile(e) {
  const file = e.target.files[0]
  if (!file) return
  fileName.value      = file.name
  parseError.value    = ''
  parsedRows.value    = []
  importDone.value    = false
  importedCount.value = 0
  importFailed.value  = 0

  const reader = new FileReader()
  reader.onload = ev => {
    try {
      const text  = ev.target.result
      const lines = text.replace(/\r\n/g, '\n').replace(/\r/g, '\n').trim().split('\n')
      if (lines.length < 2) { parseError.value = 'Файл пустой или нет строк данных'; return }

      const headers  = parseCSVLine(lines[0]).map(h => h.trim())
      const required = ['category', 'object_name', 'amount', 'date', 'period']
      const missing  = required.filter(h => !headers.includes(h))
      if (missing.length) { parseError.value = `Отсутствуют колонки: ${missing.join(', ')}`; return }

      parsedRows.value = lines.slice(1)
        .filter(l => l.trim())
        .map(line => {
          const vals = parseCSVLine(line)
          const row  = {}
          headers.forEach((h, i) => { row[h] = vals[i]?.trim() ?? '' })
          row._errors    = validateRow(row)
          row._duplicate = !row._errors.length && isDuplicate(row)
          return row
        })
    } catch (err) {
      parseError.value = 'Ошибка чтения файла: ' + err.message
    }
  }
  reader.readAsText(file, 'UTF-8')
}

const invalidRows  = computed(() => parsedRows.value.filter(r => r._errors.length))
const dupRows      = computed(() => parsedRows.value.filter(r => !r._errors.length && r._duplicate))
const validRows    = computed(() => parsedRows.value.filter(r => !r._errors.length && !r._duplicate))
const progressPct  = computed(() =>
  validRows.value.length ? Math.round(importedCount.value / validRows.value.length * 100) : 0
)

function isDuplicate(row) {
  const amt = Number(row.amount)
  return store.payments.some(p =>
    p.category    === row.category    &&
    p.object_name === row.object_name &&
    Number(p.amount) === amt          &&
    p.date        === row.date        &&
    p.period      === row.period
  )
}

// ── Import ──────────────────────────────────────────────────────
async function doImport() {
  importing.value     = true
  importedCount.value = 0
  importFailed.value  = 0
  importSkipped.value = dupRows.value.length
  importDone.value    = false

  for (const row of validRows.value) {
    try {
      await api.createPayment({
        category:    row.category,
        object_name: row.object_name,
        amount:      Number(row.amount),
        date:        row.date,
        period:      row.period,
        note:        row.note || '',
      })
      importedCount.value++
    } catch {
      importFailed.value++
    }
  }

  importing.value  = false
  importDone.value = true
  await store.fetchStats()
  await store.fetchPayments()
}
</script>

<style scoped>
.ie-root { display: flex; flex-direction: column; gap: 12px; padding: 0 16px 24px; }

.ie-card {
  background: var(--bg-card);
  border-radius: 14px;
  padding: 16px;
  border: 1px solid var(--border);
}

.ie-title {
  font-size: 14px; font-weight: 700; color: var(--text-primary);
  margin-bottom: 6px;
}
.ie-hint {
  font-size: 12px; color: var(--text-secondary);
  margin: 0 0 14px; line-height: 1.6;
}
.ie-hint code {
  font-family: monospace; font-size: 11px;
  background: var(--bg-input); padding: 2px 5px; border-radius: 4px;
  color: var(--accent-blue);
}

/* Buttons */
.ie-btn {
  width: 100%; padding: 13px; border: none; border-radius: 14px;
  font-size: 14px; font-weight: 700; cursor: pointer;
  font-family: inherit; transition: opacity .2s;
}
.ie-btn:disabled { opacity: .4; cursor: default; }
.ie-btn--green { background: var(--accent-green); color: #000; }
.ie-btn--blue  { background: var(--accent-blue); color: #fff; margin-top: 12px; }

/* Dropzone */
.ie-dropzone input { display: none; }
.ie-dropzone-inner {
  border: 2px dashed var(--border);
  border-radius: 12px; padding: 20px 16px;
  text-align: center; cursor: pointer;
  color: var(--text-secondary); font-size: 13px; line-height: 1.7;
  transition: border-color .2s;
  margin-bottom: 14px;
}
.ie-dropzone-inner.has-file  { border-color: var(--accent-blue); color: var(--text-primary); }
.ie-dropzone-inner:hover     { border-color: var(--accent-blue); }
.ie-dropzone-icon { font-size: 24px; margin-bottom: 4px; }

/* Parse error */
.ie-parse-error {
  color: var(--accent-red); font-size: 12px;
  background: rgba(255,69,58,.1); border-radius: 10px;
  padding: 10px 12px; margin-bottom: 12px;
}

/* Preview table */
.ie-table-wrap {
  overflow-x: auto;
  border-radius: 10px;
  border: 1px solid var(--border);
  margin-bottom: 10px;
}
.ie-table {
  width: 100%; border-collapse: collapse; font-size: 11px;
}
.ie-table th {
  background: var(--bg-secondary); color: var(--text-secondary);
  padding: 7px 8px; text-align: left; font-weight: 700;
  text-transform: uppercase; letter-spacing: .5px; white-space: nowrap;
}
.ie-table td { padding: 8px; border-top: 1px solid var(--border); white-space: nowrap; }
.tr--err td  { background: rgba(255,69,58,.06); }
.td-num      { color: var(--text-secondary); }

/* Badges */
.ie-badge {
  display: inline-flex; width: 20px; height: 20px;
  border-radius: 50%; align-items: center; justify-content: center;
  font-size: 10px; font-weight: 700;
}
.ie-badge--ok  { background: rgba(48,209,88,.15); color: var(--accent-green); }
.ie-badge--err { background: rgba(255,69,58,.15); color: var(--accent-red); }

/* Stats */
.ie-stats { display: flex; gap: 12px; font-size: 13px; font-weight: 600; margin-bottom: 10px; }
.ie-stat-ok  { color: var(--accent-green); }
.ie-stat-err { color: var(--accent-red); }

/* Progress */
.ie-progress-wrap { margin-bottom: 10px; }
.ie-progress-track {
  height: 4px; background: var(--bg-input);
  border-radius: 2px; overflow: hidden; margin-bottom: 4px;
}
.ie-progress-fill {
  height: 100%; background: var(--accent-blue);
  transition: width .3s; border-radius: 2px;
}
.ie-progress-txt { font-size: 11px; color: var(--text-secondary); text-align: center; }

/* Result */
.ie-done { font-size: 13px; color: var(--accent-green); font-weight: 600; margin-bottom: 4px; }
.ie-skip { font-size: 13px; color: var(--accent-orange); margin-bottom: 4px; }
.ie-fail { font-size: 13px; color: var(--accent-red); margin-bottom: 6px; }

/* Duplicate rows */
.tr--dup td { background: rgba(255,159,10,.06); }
.ie-badge--dup { background: rgba(255,159,10,.15); color: var(--accent-orange); }
.ie-stat-dup { color: var(--accent-orange); }

/* Clear DB card */
.ie-card--danger { border-color: rgba(255,69,58,.3); }
.ie-btn--red   { background: var(--accent-red); color: #fff; }
.ie-btn--ghost {
  background: var(--bg-input); color: var(--text-primary);
  border: 1px solid var(--border);
}
.ie-confirm-txt {
  font-size: 13px; color: var(--text-secondary);
  margin: 0 0 12px; line-height: 1.5;
}
.ie-confirm-txt--warn { color: var(--accent-red); font-weight: 600; }
.ie-confirm-btns { display: flex; gap: 10px; }
.ie-confirm-btns .ie-btn { margin-top: 0; }
</style>
