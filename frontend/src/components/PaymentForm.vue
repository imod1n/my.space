<template>
  <div class="payment-form">
    <h2 class="form-title">Новый платёж</h2>

    <!-- Объект -->
    <div class="field">
      <label>Объект</label>
      <div class="custom-select" :class="{ open: openDropdown === 'object' }" @click.stop="toggleDropdown('object')">
        <div class="select-trigger">
          <span class="select-icon">{{ selectedObject.icon }}</span>
          <span class="select-label">{{ selectedObject.name }}</span>
          <svg class="select-arrow" width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M3 5L7 9L11 5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <Transition name="dropdown">
          <div v-if="openDropdown === 'object'" class="select-menu" @click.stop>
            <div
              v-for="o in OBJECTS" :key="o.name"
              class="select-option"
              :class="{ selected: form.object_name === o.name }"
              @click="form.object_name = o.name; openDropdown = null"
            >
              <span class="option-icon">{{ o.icon }}</span>
              <span>{{ o.name }}</span>
              <svg v-if="form.object_name === o.name" class="check" width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M2.5 7L5.5 10L11.5 4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>
        </Transition>
      </div>
    </div>

    <!-- Категория -->
    <div class="field">
      <label>Категория</label>
      <div class="custom-select" :class="{ open: openDropdown === 'category' }" @click.stop="toggleDropdown('category')">
        <div class="select-trigger">
          <span class="select-icon" :style="{ background: selectedCategory.color + '22', color: selectedCategory.color, borderRadius: '8px', padding: '4px' }">{{ selectedCategory.icon }}</span>
          <span class="select-label">{{ selectedCategory.name }}</span>
          <svg class="select-arrow" width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M3 5L7 9L11 5" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <Transition name="dropdown">
          <div v-if="openDropdown === 'category'" class="select-menu" @click.stop>
            <div
              v-for="c in CATEGORIES" :key="c.name"
              class="select-option"
              :class="{ selected: form.category === c.name }"
              @click="form.category = c.name; openDropdown = null"
            >
              <span class="option-icon" :style="{ background: c.color + '22', color: c.color }">{{ c.icon }}</span>
              <span>{{ c.name }}</span>
              <svg v-if="form.category === c.name" class="check" width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M2.5 7L5.5 10L11.5 4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>
        </Transition>
      </div>
    </div>

    <!-- Даты в ряд -->
    <div class="field-row">
      <div class="field">
        <label>Дата платежа</label>
        <div class="date-wrapper">
          <input type="date" v-model="form.date" />
          <button
            v-if="form.date"
            class="date-clear"
            title="Очистить дату"
            type="button"
            @click="form.date = ''"
          >
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
              <path d="M2 2L10 10M10 2L2 10" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
      </div>
      <div class="field">
        <label>За период</label>
        <input type="month" v-model="form.period" />
      </div>
    </div>

    <!-- Сумма -->
    <div class="field">
      <label>Сумма, ₽</label>
      <input
        type="number"
        inputmode="decimal"
        v-model.number="form.amount"
        placeholder="0.00"
        step="0.01"
        min="0"
      />
    </div>

    <!-- Комментарий -->
    <div class="field">
      <label>Комментарий <span class="optional">(необязательно)</span></label>
      <input type="text" v-model="form.note" placeholder="Показания счётчика, дополнения…" />
    </div>

    <div v-if="error" class="error-msg">{{ error }}</div>

    <button class="btn-submit" :disabled="loading" @click="submit">
      <span v-if="loading">Сохраняем…</span>
      <span v-else>Добавить платёж</span>
    </button>
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted, onUnmounted } from 'vue'
import { usePaymentsStore, OBJECTS, CATEGORIES } from '../stores/payments'

const store   = usePaymentsStore()
const loading = ref(false)
const error   = ref('')

// ── Dropdown ───────────────────────────────────────────────
const openDropdown = ref(null)

const selectedObject   = computed(() => OBJECTS.find(o => o.name === form.object_name)   || OBJECTS[0])
const selectedCategory = computed(() => CATEGORIES.find(c => c.name === form.category)   || CATEGORIES[0])

function toggleDropdown(name) {
  openDropdown.value = openDropdown.value === name ? null : name
}

function closeDropdown() { openDropdown.value = null }

onMounted(()   => document.addEventListener('click', closeDropdown))
onUnmounted(() => document.removeEventListener('click', closeDropdown))

// ── Form ───────────────────────────────────────────────────
function todayStr() {
  return new Date().toISOString().split('T')[0]
}
function prevMonthStr() {
  const d = new Date()
  d.setMonth(d.getMonth() - 1)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
}

const form = reactive({
  object_name: OBJECTS[0].name,
  category:    CATEGORIES[0].name,
  date:        todayStr(),
  period:      prevMonthStr(),
  amount:      null,
  note:        '',
})

async function submit() {
  error.value = ''
  if (!form.amount || form.amount <= 0) {
    error.value = 'Введите сумму'
    return
  }
  loading.value = true
  try {
    await store.addPayment({ ...form })
    form.amount = null
    form.note   = ''
    store.currentPeriod = form.period
    await store.fetchStats()
    emit('added')
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Ошибка сохранения'
  } finally {
    loading.value = false
  }
}

const emit = defineEmits(['added'])
</script>

<style scoped>
.payment-form {
  padding: 16px;
}
.form-title {
  font-size: 17px;
  font-weight: 700;
  margin-bottom: 20px;
  color: var(--text-primary);
}
.field {
  margin-bottom: 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 14px;
}
label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.6px;
}
.optional {
  font-weight: 400;
  text-transform: none;
  letter-spacing: 0;
}
input {
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: 14px;
  color: var(--text-primary);
  padding: 13px 14px;
  font-size: 16px;
  font-family: inherit;
  outline: none;
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  transition: border-color .2s, box-shadow .2s;
}
input:focus {
  border-color: var(--accent-blue);
  box-shadow: 0 0 0 3px rgba(10, 132, 255, 0.12);
}
input[type="date"]::-webkit-calendar-picker-indicator,
input[type="month"]::-webkit-calendar-picker-indicator {
  filter: invert(0.7);
  cursor: pointer;
}

/* ── Date clear button ── */
.date-wrapper {
  position: relative;
}
.date-wrapper input {
  padding-right: 39px;
}
.date-clear {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  width: 22px; height: 22px;
  border: none; border-radius: 50%;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  opacity: 0.7;
  transition: opacity .15s, background .15s, color .15s;
  flex-shrink: 0;
}
.date-clear:hover {
  opacity: 1;
  background: rgba(255,69,58,.15);
  color: var(--accent-red);
}
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
input[type="number"] {
  -moz-appearance: textfield;
  appearance: textfield;
}

/* ── Custom Select ── */
.custom-select {
  position: relative;
}
.select-trigger {
  display: flex; align-items: center; gap: 10px;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 13px 14px;
  cursor: pointer;
  transition: border-color .2s, box-shadow .2s;
  user-select: none;
}
.custom-select.open .select-trigger,
.select-trigger:hover {
  border-color: var(--accent-blue);
  box-shadow: 0 0 0 3px rgba(10, 132, 255, 0.12);
}
.select-icon {
  font-size: 18px; line-height: 1; flex-shrink: 0;
}
.select-label {
  flex: 1; font-size: 15px; font-weight: 500; color: var(--text-primary);
}
.select-arrow {
  color: var(--text-secondary);
  transition: transform .25s cubic-bezier(.4,0,.2,1);
  flex-shrink: 0;
}
.custom-select.open .select-arrow {
  transform: rotate(180deg);
}
.select-menu {
  position: absolute; top: calc(100% + 6px); left: 0; right: 0;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 16px;
  overflow: hidden;
  z-index: 50;
  box-shadow: 0 8px 32px rgba(0,0,0,.5), 0 2px 8px rgba(0,0,0,.3);
}
.select-option {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 14px;
  cursor: pointer;
  transition: background .15s;
  font-size: 14px; font-weight: 500;
  color: var(--text-primary);
}
.select-option:hover    { background: var(--bg-input); }
.select-option.selected { color: var(--accent-blue); }
.select-option + .select-option { border-top: 1px solid var(--border); }
.option-icon {
  width: 30px; height: 30px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: 15px; flex-shrink: 0;
  background: var(--bg-input);
}
.check { margin-left: auto; color: var(--accent-blue); }

/* ── Dropdown animation ── */
.dropdown-enter-active { transition: all .2s cubic-bezier(.4,0,.2,1); }
.dropdown-leave-active { transition: all .15s cubic-bezier(.4,0,.2,1); }
.dropdown-enter-from, .dropdown-leave-to {
  opacity: 0; transform: translateY(-6px) scale(0.98);
}

/* ── Submit ── */
.error-msg {
  color: var(--accent-red);
  font-size: 13px;
  margin-bottom: 10px;
}
.btn-submit {
  width: 100%;
  background: var(--accent-green);
  color: #000;
  border: none;
  border-radius: 14px;
  padding: 15px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: opacity .2s;
  margin-top: 4px;
}
.btn-submit:disabled { opacity: .5; }
</style>
