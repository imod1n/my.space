<template>
  <Teleport to="body">
    <div class="bas-backdrop" @click.self="$emit('close')">
      <div class="bas-sheet">

        <!-- Header -->
        <div class="bas-header">
          <div class="bas-title-row">
            <span class="bas-type-icon">{{ typeMeta.icon }}</span>
            <span class="bas-name">{{ account.name }}</span>
          </div>
          <div class="bas-header-actions">
            <button class="bas-advance-icon" @click="showAdvance = true" title="Аванс">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="16"/>
                <line x1="8" y1="12" x2="16" y2="12"/>
              </svg>
            </button>
            <button class="bas-close" @click="$emit('close')">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
        </div>

        <BudgetAdvanceSheet
          v-if="showAdvance"
          :account="account"
          @close="showAdvance = false"
          @saved="onAdvanceSaved"
        />

        <!-- Inputs -->
        <div class="bas-fields">
          <div class="bas-field">
            <label class="bas-label">Баланс на начало периода</label>
            <div class="bas-input-wrap">
              <input
                v-model="localStart"
                type="number"
                inputmode="decimal"
                class="bas-input"
                placeholder="0"
                step="0.01"
              />
              <span class="bas-currency">₽</span>
            </div>
          </div>

          <div class="bas-field">
            <label class="bas-label">Текущий баланс</label>
            <div class="bas-input-wrap">
              <input
                v-model="localCurrent"
                type="number"
                inputmode="decimal"
                class="bas-input"
                placeholder="0"
                step="0.01"
                ref="currentInput"
              />
              <span class="bas-currency">₽</span>
            </div>
          </div>
        </div>

        <!-- Delta preview -->
        <div class="bas-delta" v-if="delta !== 0">
          <span class="bas-delta-label">Изменение:</span>
          <span class="bas-delta-value" :style="{ color: deltaColor }">{{ fmtDelta(delta) }}</span>
        </div>

        <!-- Save -->
        <button class="bas-save" :disabled="saving" @click="save">
          {{ saving ? 'Сохраняю...' : 'Сохранить' }}
        </button>

      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useBudgetStore } from '../stores/budget'
import BudgetAdvanceSheet from './BudgetAdvanceSheet.vue'

const props = defineProps({
  account: { type: Object, required: true },
})
const emit = defineEmits(['close', 'saved'])
const store = useBudgetStore()

const TYPE_META = {
  debit:   { icon: '💳' },
  credit:  { icon: '💸' },
  savings: { icon: '🏦' },
  cash:    { icon: '💵' },
  foreign: { icon: '💱' },
  invest:  { icon: '📈' },
  deposit: { icon: '🏛️' },
  other:   { icon: '📂' },
}

const typeMeta    = computed(() => TYPE_META[props.account.type] ?? { icon: '💰' })
const localStart   = ref(props.account.balance_start)
const localCurrent = ref(props.account.balance_current)
const saving       = ref(false)
const currentInput = ref(null)
const showAdvance  = ref(false)

const delta = computed(() => Number(localCurrent.value) - Number(localStart.value))
const deltaColor = computed(() => delta.value > 0 ? '#30d158' : delta.value < 0 ? '#ff453a' : '#8e8e93')

function fmt(n) { return Math.round(Number(n)).toLocaleString('ru-RU') + ' ₽' }
function fmtDelta(n) {
  const v = Math.round(Number(n))
  return (v > 0 ? '+' : '') + v.toLocaleString('ru-RU') + ' ₽'
}

async function save() {
  saving.value = true
  try {
    await store.updateBalance(
      props.account.id,
      Number(localStart.value) || 0,
      Number(localCurrent.value) || 0,
    )
    emit('saved')
    emit('close')
  } finally {
    saving.value = false
  }
}

function onAdvanceSaved() {
  emit('saved')
  emit('close')
}

let savedScrollY = 0

onMounted(async () => {
  await nextTick()
  savedScrollY = window.scrollY
  document.body.style.position = 'fixed'
  document.body.style.top = `-${savedScrollY}px`
  document.body.style.width = '100%'
  currentInput.value?.focus()
})

onUnmounted(() => {
  document.body.style.position = ''
  document.body.style.top = ''
  document.body.style.width = ''
  window.scrollTo(0, savedScrollY)
})
</script>

<style scoped>
.bas-backdrop {
  position: fixed; inset: 0; z-index: 300;
  background: rgba(0,0,0,0.6);
  display: flex; align-items: flex-end;
}

.bas-sheet {
  width: 100%;
  background: var(--bg-secondary);
  border-radius: 20px 20px 0 0;
  border-top: 1px solid var(--border);
  padding: 20px 20px calc(24px + env(safe-area-inset-bottom, 0px));
  animation: slideUp .25s ease;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

@keyframes slideUp {
  from { transform: translateY(100%); }
  to   { transform: translateY(0); }
}

.bas-header {
  display: flex; align-items: center; justify-content: space-between;
}
.bas-title-row {
  display: flex; align-items: center; gap: 10px;
}
.bas-type-icon { font-size: 22px; }
.bas-name { font-size: 17px; font-weight: 600; color: var(--text-primary); }

.bas-header-actions {
  display: flex; align-items: center; gap: 8px;
}

.bas-advance-icon {
  width: 30px; height: 30px; border-radius: 50%;
  background: var(--bg-input); border: none;
  color: var(--accent-blue); cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background .15s;
}
.bas-advance-icon:hover { background: var(--border); }

.bas-close {
  width: 30px; height: 30px; border-radius: 50%;
  background: var(--bg-input); border: none;
  color: var(--text-secondary); cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background .15s;
}
.bas-close:hover { background: var(--border); color: #fff; }

.bas-fields { display: flex; flex-direction: column; gap: 12px; }

.bas-field { display: flex; flex-direction: column; gap: 6px; }
.bas-label {
  font-size: 12px; font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase; letter-spacing: .4px;
}

.bas-input-wrap {
  display: flex; align-items: center; gap: 8px;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 0 14px;
}
.bas-input {
  flex: 1;
  background: transparent; border: none; outline: none;
  font-size: 20px; font-weight: 600;
  color: var(--text-primary);
  font-family: inherit;
  padding: 14px 0;
  font-variant-numeric: tabular-nums;
  -moz-appearance: textfield;
}
.bas-input::-webkit-inner-spin-button,
.bas-input::-webkit-outer-spin-button { -webkit-appearance: none; }
.bas-currency {
  font-size: 18px; font-weight: 600;
  color: var(--text-secondary);
}

.bas-delta {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 14px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 10px;
}
.bas-delta-label { font-size: 13px; color: var(--text-secondary); }
.bas-delta-value { font-size: 15px; font-weight: 700; font-variant-numeric: tabular-nums; margin-left: auto; }

.bas-save {
  width: 100%;
  padding: 16px;
  border-radius: 14px;
  background: var(--accent-green);
  color: #000;
  font-size: 16px; font-weight: 700;
  border: none; cursor: pointer;
  transition: opacity .15s, transform .1s;
}
.bas-save:active { transform: scale(0.98); }
.bas-save:disabled { opacity: 0.5; cursor: default; }

</style>
