<template>
  <div>
  <div class="stats-table">

    <!-- Toggle -->
    <div class="view-toggle">
      <button :class="{ active: view === 'categories' }" @click="view = 'categories'">
        По категориям
      </button>
      <button :class="{ active: view === 'objects' }" @click="view = 'objects'">
        По объектам
      </button>
    </div>

    <!-- ── BY CATEGORIES ── -->
    <template v-if="view === 'categories'">
      <div v-if="catRows.length === 0" class="empty">Нет платежей за этот период</div>
      <div v-else class="cat-list">
        <div
          v-for="row in catRows"
          :key="row.name"
          class="cat-row"
        >
          <div class="cat-icon" :style="{ background: row.color + '22', color: row.color }">
            {{ row.icon }}
          </div>
          <div class="cat-info">
            <div class="cat-name">{{ row.name }}</div>
          </div>
          <div class="cat-amount">{{ fmt(row.amount) }}</div>
        </div>
      </div>
    </template>

    <!-- ── BY OBJECTS ── -->
    <template v-else>
      <div v-if="objKeys.length === 0" class="empty">Нет платежей за этот период</div>
      <div v-else>
        <div
          v-for="obj in objKeys"
          :key="obj"
          class="obj-block"
        >
          <!-- Object header -->
          <div class="obj-header" @click="toggleObj(obj)">
            <span class="obj-icon">{{ getObjMeta(obj).icon }}</span>
            <span class="obj-name">{{ obj }}</span>
            <span class="obj-total">{{ fmt(objTotal(obj)) }}</span>
            <span class="obj-arrow" :class="{ open: openObjs.has(obj) }">›</span>
          </div>

          <!-- Payment rows for this object -->
          <transition name="slide">
            <div v-if="openObjs.has(obj)" class="obj-rows">
              <div class="obj-row-head">
                <span class="center">Категория</span>
                <span class="center">Дата платежа</span>
                <span class="center">За период</span>
                <span class="center">Сумма</span>
                <span></span>
              </div>
              <div
                v-for="(row, i) in byObject[obj]"
                :key="i"
                class="obj-row"
              >
                <div class="cat-badge">
                  <span
                    class="dot"
                    :style="{ background: getCatMeta(row.category).color }"
                  ></span>
                  {{ row.category }}
                </div>
                <div class="date-val center">{{ fmtDate(row.date) }}</div>
                <div class="period-val center">{{ fmtPeriod(row.period) }}</div>
                <div class="amount-val center">{{ fmt(row.amount) }}</div>
                <div class="row-actions">
                  <button
                    v-if="!row.date"
                    class="act-btn act-btn--today"
                    title="Поставить сегодняшнюю дату"
                    @click.stop="setTodayDate(row)"
                  >
                    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                      <rect x="1.5" y="2.5" width="11" height="10" rx="2" stroke="currentColor" stroke-width="1.4"/>
                      <path d="M4.5 1v3M9.5 1v3" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
                      <path d="M1.5 6h11" stroke="currentColor" stroke-width="1.4"/>
                      <circle cx="7" cy="9.5" r="1" fill="currentColor"/>
                    </svg>
                  </button>
                  <button
                    class="act-btn"
                    :class="{ 'act-btn--dim': !row.note }"
                    :title="row.note ? 'Комментарий' : 'Нет комментария'"
                    @click.stop="row.note && openDetail(row)"
                  >
                    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                      <circle cx="7" cy="7" r="6" stroke="currentColor" stroke-width="1.4"/>
                      <rect x="6.3" y="6" width="1.4" height="4.5" rx="0.7" fill="currentColor"/>
                      <circle cx="7" cy="3.8" r="0.8" fill="currentColor"/>
                    </svg>
                  </button>
                  <button
                    class="act-btn act-btn--edit"
                    title="Редактировать"
                    @click.stop="openEdit(row)"
                  >
                    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                      <path d="M9.5 2.5L11.5 4.5L5 11H3V9L9.5 2.5Z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/>
                    </svg>
                  </button>
                  <button
                    class="act-btn act-btn--del"
                    title="Удалить"
                    @click.stop="confirmDelete(row)"
                  >
                    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                      <path d="M2.5 4H11.5M5 4V2.5H9V4M5.5 6.5V10M8.5 6.5V10M3.5 4L4.5 11.5H9.5L10.5 4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </transition>
        </div>
      </div>
    </template>

  </div><!-- /stats-table -->

  <!-- ── DETAIL MODAL ── -->
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="detailRow" class="modal-backdrop" @click.self="detailRow = null">
        <div class="modal-sheet">
          <div class="modal-header">
            <span class="modal-title">Комментарий</span>
            <button class="modal-close" @click="detailRow = null">
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <path d="M4 4L14 14M14 4L4 14" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
              </svg>
            </button>
          </div>
          <div class="modal-body">
            <div class="detail-meta">
              <span class="detail-cat">
                <span class="dot" :style="{ background: getCatMeta(detailRow.category).color }"></span>
                {{ detailRow.category }}
              </span>
              <span class="detail-amount">{{ fmt(detailRow.amount) }}</span>
            </div>
            <div class="detail-note">{{ detailRow.note }}</div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>

  <!-- ── EDIT MODAL ── -->
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="editRow" class="modal-backdrop" @click.self="cancelEdit">
        <div class="modal-sheet">
          <div class="modal-header">
            <span class="modal-title">Редактировать платёж</span>
            <button class="modal-close" @click="cancelEdit">
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                <path d="M4 4L14 14M14 4L4 14" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
              </svg>
            </button>
          </div>
          <div class="modal-body">
            <div class="edit-field">
              <label>Сумма, ₽</label>
              <input type="number" inputmode="decimal" v-model.number="editForm.amount" step="0.01" min="0" />
            </div>
            <div class="edit-field-row">
              <div class="edit-field">
                <label>Дата платежа</label>
                <input type="date" v-model="editForm.date" />
              </div>
              <div class="edit-field">
                <label>За период</label>
                <input type="month" v-model="editForm.period" />
              </div>
            </div>
            <div class="edit-field">
              <label>Комментарий</label>
              <input type="text" v-model="editForm.note" placeholder="Необязательно" />
            </div>
            <div v-if="editError" class="edit-error">{{ editError }}</div>
            <button class="btn-save" :disabled="editLoading" @click="saveEdit">
              <span v-if="editLoading">Сохраняем…</span>
              <span v-else>Сохранить</span>
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>

  <!-- ── DELETE CONFIRM MODAL ── -->
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="deleteRow" class="modal-backdrop" @click.self="deleteRow = null">
        <div class="modal-sheet modal-sheet--sm">
          <div class="modal-header">
            <span class="modal-title">Удалить платёж?</span>
          </div>
          <div class="modal-body">
            <div class="detail-meta">
              <span class="detail-cat">
                <span class="dot" :style="{ background: getCatMeta(deleteRow.category).color }"></span>
                {{ deleteRow.category }}
              </span>
              <span class="detail-amount">{{ fmt(deleteRow.amount) }}</span>
            </div>
            <p class="delete-hint">Действие нельзя отменить.</p>
            <div class="delete-actions">
              <button class="btn-cancel" @click="deleteRow = null">Отмена</button>
              <button class="btn-delete" :disabled="deleteLoading" @click="doDelete">
                <span v-if="deleteLoading">Удаляем…</span>
                <span v-else>Удалить</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
  </div><!-- /root -->
</template>

<script setup>
import { ref, computed, watch, reactive } from 'vue'
import { usePaymentsStore, getCatMeta, getObjMeta, OBJECTS } from '../stores/payments'

const store = usePaymentsStore()
const view  = ref('objects')

// Which object blocks are expanded
const openObjs = ref(new Set())
function toggleObj(name) {
  if (openObjs.value.has(name)) openObjs.value.delete(name)
  else openObjs.value.add(name)
  openObjs.value = new Set(openObjs.value) // trigger reactivity
}

// Auto-expand objects that have rows when data loads
watch(() => store.stats, (s) => {
  if (!s) return
  openObjs.value = new Set(Object.keys(s.by_object || {}))
}, { immediate: true })

// ── By categories ────────────────────────────────────────────
const catRows = computed(() => {
  const bc = store.stats?.by_category || {}
  return Object.entries(bc)
    .map(([name, amount]) => ({ name, amount, ...getCatMeta(name) }))
    .sort((a, b) => b.amount - a.amount)
})

// ── By objects ───────────────────────────────────────────────
const byObject = computed(() => store.stats?.by_object || {})

// Show all 4 objects in canonical order; empty ones at the bottom
const objKeys = computed(() => {
  const bo = byObject.value
  const withData    = OBJECTS.map(o => o.name).filter(n => bo[n]?.length)
  const withoutData = OBJECTS.map(o => o.name).filter(n => !bo[n]?.length)
  return [...withData, ...withoutData]
})

function objTotal(name) {
  return (byObject.value[name] || []).reduce((s, r) => s + r.amount, 0)
}

// ── Formatters ───────────────────────────────────────────────
const MONTHS_RU = ['Январь','Февраль','Март','Апрель','Май','Июнь',
                   'Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь']

function fmt(n) {
  return Number(n).toLocaleString('ru-RU') + ' ₽'
}
function fmtDate(d) {
  if (!d) return '—'
  const [y, m, dd] = d.split('-')
  return `${dd}.${m}.${y}`
}
function fmtPeriod(p) {
  if (!p) return '—'
  const [y, m] = p.split('-')
  return MONTHS_RU[parseInt(m) - 1] + ' ' + y
}

// ── Detail modal ─────────────────────────────────────────────
const detailRow = ref(null)
function openDetail(row) { detailRow.value = row }

// ── Edit modal ───────────────────────────────────────────────
const editRow     = ref(null)
const editLoading = ref(false)
const editError   = ref('')
const editForm    = reactive({ amount: null, date: '', period: '', note: '' })

function openEdit(row) {
  editRow.value     = row
  editForm.amount   = row.amount
  editForm.date     = row.date
  editForm.period   = row.period
  editForm.note     = row.note || ''
  editError.value   = ''
}
function cancelEdit() { editRow.value = null }

async function saveEdit() {
  editError.value = ''
  if (!editForm.amount || editForm.amount <= 0) {
    editError.value = 'Введите сумму'
    return
  }
  editLoading.value = true
  try {
    await store.updatePayment(editRow.value.id, {
      amount: editForm.amount,
      date:   editForm.date,
      period: editForm.period,
      note:   editForm.note,
    })
    editRow.value = null
  } catch (e) {
    editError.value = e?.response?.data?.detail || 'Ошибка сохранения'
  } finally {
    editLoading.value = false
  }
}

// ── Set today's date ─────────────────────────────────────────
async function setTodayDate(row) {
  const today = new Date().toISOString().slice(0, 10) // YYYY-MM-DD
  await store.updatePayment(row.id, {
    amount: row.amount,
    date:   today,
    period: row.period,
    note:   row.note || '',
  })
}

// ── Delete modal ─────────────────────────────────────────────
const deleteRow     = ref(null)
const deleteLoading = ref(false)

function confirmDelete(row) { deleteRow.value = row }

async function doDelete() {
  deleteLoading.value = true
  try {
    await store.deletePayment(deleteRow.value.id)
    deleteRow.value = null
  } finally {
    deleteLoading.value = false
  }
}
</script>

<style scoped>
.stats-table { padding: 0 16px 24px; }

/* Toggle */
.view-toggle {
  display: flex; gap: 4px;
  background: var(--bg-card);
  border-radius: 10px; padding: 4px;
  margin-bottom: 16px;
}
.view-toggle button {
  flex: 1; padding: 8px 10px; border: none;
  background: transparent; color: var(--text-secondary);
  border-radius: 8px; font-size: 13px; font-weight: 600;
  cursor: pointer; transition: all .2s; font-family: inherit;
}
.view-toggle button.active {
  background: var(--bg-secondary); color: var(--text-primary);
  box-shadow: 0 1px 4px rgba(0,0,0,.5);
}

.empty { color: var(--text-secondary); font-size: 14px; text-align: center; padding: 32px 0; }

/* Category rows */
.cat-list { display: flex; flex-direction: column; gap: 8px; }
.cat-row {
  display: flex; align-items: center; gap: 12px;
  background: var(--bg-card); border-radius: 12px; padding: 12px 14px;
}
.cat-icon {
  width: 36px; height: 36px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; flex-shrink: 0;
}
.cat-info { flex: 1; }
.cat-name { font-size: 14px; font-weight: 600; }
.cat-amount { font-size: 15px; font-weight: 700; color: var(--accent-green); }

/* Object blocks */
.obj-block {
  background: var(--bg-card); border-radius: 14px;
  margin-bottom: 10px; overflow: hidden;
  border: 1px solid var(--border);
}
.obj-header {
  display: flex; align-items: center; gap: 10px;
  padding: 14px 16px; cursor: pointer; user-select: none;
  transition: background .15s;
}
.obj-header:active { background: var(--bg-input); }
.obj-icon { font-size: 18px; }
.obj-name { flex: 1; font-size: 14px; font-weight: 700; }
.obj-total { font-size: 14px; font-weight: 700; color: var(--accent-green); }
.obj-arrow {
  color: var(--text-secondary); font-size: 16px;
  transition: transform .2s; display: inline-block;
}
.obj-arrow.open { transform: rotate(90deg); }

.obj-rows { border-top: 1px solid var(--border); }
.obj-row-head {
  display: grid;
  grid-template-columns: 1fr 94px 86px 96px 82px;
  gap: 4px;
  padding: 7px 16px;
  font-size: 10px; font-weight: 700;
  color: var(--text-secondary);
  text-transform: uppercase; letter-spacing: .7px;
  background: var(--bg-secondary);
}
.obj-row {
  display: grid;
  grid-template-columns: 1fr 94px 86px 96px 82px;
  gap: 4px;
  padding: 11px 16px;
  font-size: 12px;
  border-top: 1px solid var(--border);
  align-items: center;
  transition: background .12s;
}
.obj-row:hover { background: rgba(255,255,255,0.03); }
.cat-badge { display: flex; align-items: center; gap: 6px; }
.dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.date-val { color: var(--text-secondary); font-size: 12px; }
.period-val { color: var(--accent-blue); font-size: 11px; }
.amount-val { font-weight: 700; font-size: 13px; }
.right  { text-align: right; }
.center { text-align: center; }

/* Action buttons */
.row-actions {
  display: flex; align-items: center; gap: 3px; justify-content: flex-end;
}
.act-btn {
  width: 24px; height: 24px; border-radius: 6px; border: none;
  background: transparent; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  color: var(--text-secondary);
  transition: background .15s, color .15s;
  flex-shrink: 0;
}
.act-btn:hover { background: var(--bg-input); color: #fff; }
.act-btn--dim { opacity: 0.25; cursor: default; }
.act-btn--dim:hover { background: transparent; color: var(--text-secondary); }
.act-btn--edit:hover  { background: rgba(10,132,255,.15); color: var(--accent-blue); }
.act-btn--del:hover   { background: rgba(255,69,58,.15);  color: var(--accent-red); }
.act-btn--today       { color: var(--accent-orange); }
.act-btn--today:hover { background: rgba(255,159,10,.15); color: var(--accent-orange); }

/* Slide transition */
.slide-enter-active, .slide-leave-active { transition: all .2s ease; overflow: hidden; }
.slide-enter-from, .slide-leave-to { max-height: 0; opacity: 0; }
.slide-enter-to, .slide-leave-from { max-height: 800px; opacity: 1; }

/* ── Modals ── */
.modal-backdrop {
  position: fixed; inset: 0; z-index: 200;
  background: rgba(0,0,0,0.6);
  display: flex; align-items: flex-end; justify-content: center;
  padding: 0 0 env(safe-area-inset-bottom, 0);
}
.modal-sheet {
  width: 100%; max-width: 520px;
  background: var(--bg-secondary);
  border-radius: 20px 20px 0 0;
  border-top: 1px solid var(--border);
  padding-bottom: 20px;
}
.modal-sheet--sm { max-width: 420px; }
.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 18px 20px 14px;
  border-bottom: 1px solid var(--border);
}
.modal-title { font-size: 15px; font-weight: 700; color: var(--text-primary); }
.modal-close {
  width: 30px; height: 30px; border-radius: 50%; border: none;
  background: var(--bg-input); cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  color: var(--text-secondary);
}
.modal-close:hover { color: #fff; }
.modal-body { padding: 16px 20px; }

/* Detail */
.detail-meta {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 14px;
}
.detail-cat { display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 600; }
.detail-amount { font-size: 15px; font-weight: 700; color: var(--accent-green); }
.detail-note {
  background: var(--bg-card); border-radius: 12px;
  padding: 14px; font-size: 14px; line-height: 1.5;
  color: var(--text-primary); white-space: pre-wrap;
}

/* Edit form */
.edit-field {
  margin-bottom: 12px;
  display: flex; flex-direction: column; gap: 6px;
}
.edit-field-row {
  display: grid; grid-template-columns: 1fr 1fr; gap: 10px;
  margin-bottom: 12px;
}
.edit-field label {
  font-size: 11px; font-weight: 700; text-transform: uppercase;
  letter-spacing: .6px; color: var(--text-secondary);
}
.edit-field input {
  background: var(--bg-input); border: 1px solid var(--border);
  border-radius: 12px; color: var(--text-primary);
  padding: 11px 13px; font-size: 16px; font-family: inherit;
  outline: none; -webkit-appearance: none; appearance: none; width: 100%;
  transition: border-color .2s;
}
.edit-field input:focus { border-color: var(--accent-blue); }
.edit-field input[type="date"]::-webkit-calendar-picker-indicator,
.edit-field input[type="month"]::-webkit-calendar-picker-indicator { filter: invert(0.7); }
.edit-field input[type="number"]::-webkit-inner-spin-button,
.edit-field input[type="number"]::-webkit-outer-spin-button { -webkit-appearance: none; }
.edit-error { color: var(--accent-red); font-size: 13px; margin-bottom: 10px; }

/* Delete */
.delete-hint { font-size: 13px; color: var(--text-secondary); margin: 8px 0 16px; }
.delete-actions { display: flex; gap: 10px; }
.btn-cancel, .btn-save, .btn-delete {
  flex: 1; padding: 13px; border: none; border-radius: 14px;
  font-size: 15px; font-weight: 700; cursor: pointer;
  font-family: inherit; transition: opacity .2s;
}
.btn-cancel { background: var(--bg-input); color: var(--text-primary); }
.btn-save   { background: var(--accent-green); color: #000; width: 100%; }
.btn-delete { background: var(--accent-red); color: #fff; }
.btn-save:disabled, .btn-delete:disabled { opacity: .5; }

/* Modal transition */
.modal-enter-active, .modal-leave-active { transition: all .25s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .modal-sheet, .modal-leave-to .modal-sheet { transform: translateY(40px); }

/* ── Mobile: card layout for object rows ── */
@media (max-width: 849px) {
  .obj-row-head { display: none; }

  .obj-row {
    display: grid;
    grid-template-areas:
      "cat    cat    amount"
      "date   period actions";
    grid-template-columns: auto 1fr auto;
    gap: 5px 8px;
    padding: 12px 14px;
  }

  .cat-badge   { grid-area: cat; font-size: 13px; }
  .date-val    { grid-area: date; text-align: left; font-size: 11px; }
  .period-val  { grid-area: period; text-align: left; font-size: 11px; }
  .amount-val  { grid-area: amount; text-align: right; font-size: 14px; align-self: center; }
  .row-actions { grid-area: actions; justify-content: flex-end; align-self: center; }
}
</style>
