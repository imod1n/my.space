<template>
  <Teleport to="body">
    <div class="adv-backdrop" @click.self="$emit('close')">
      <div class="adv-sheet">

        <!-- Header -->
        <div class="adv-header">
          <div class="adv-title-row">
            <span class="adv-type-icon">{{ typeMeta.icon }}</span>
            <span class="adv-name">{{ account.name }}</span>
          </div>
          <button class="adv-close" @click="$emit('close')">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <!-- Input -->
        <div class="adv-field">
          <label class="adv-label">Аванс</label>
          <div class="adv-input-wrap">
            <input
              v-model="advanceAmount"
              type="number"
              inputmode="decimal"
              class="adv-input"
              placeholder="0"
              step="0.01"
              ref="advInput"
            />
            <span class="adv-currency">₽</span>
          </div>
        </div>

        <button class="adv-save" :disabled="saving || !advanceAmount" @click="apply">
          {{ saving ? 'Добавляю...' : '+ К началу периода' }}
        </button>

      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useBudgetStore } from '../stores/budget'

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

const typeMeta      = computed(() => TYPE_META[props.account.type] ?? { icon: '💰' })
const advanceAmount = ref('')
const saving        = ref(false)
const advInput      = ref(null)

onMounted(async () => {
  await nextTick()
  advInput.value?.focus()
})

async function apply() {
  const amount = Number(advanceAmount.value)
  if (!amount || amount <= 0) return
  saving.value = true
  try {
    await store.addAdvance(props.account.id, amount)
    emit('saved')
    emit('close')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.adv-backdrop {
  position: fixed; inset: 0; z-index: 400;
  background: rgba(0,0,0,0.5);
  display: flex; align-items: flex-end;
}

.adv-sheet {
  width: 100%;
  background: var(--bg-secondary);
  border-radius: 20px 20px 0 0;
  border-top: 1px solid var(--border);
  padding: 20px 20px calc(24px + env(safe-area-inset-bottom, 0px));
  animation: slideUp .2s ease;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

@keyframes slideUp {
  from { transform: translateY(100%); }
  to   { transform: translateY(0); }
}

.adv-header {
  display: flex; align-items: center; gap: 8px;
}
.adv-title-row {
  display: flex; align-items: center; gap: 10px;
  flex: 1;
}
.adv-type-icon { font-size: 22px; }
.adv-name { font-size: 17px; font-weight: 600; color: var(--text-primary); }

.adv-back {
  width: 30px; height: 30px; border-radius: 50%;
  background: var(--bg-input); border: none;
  color: var(--text-secondary); cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  transition: background .15s;
}
.adv-back:hover { background: var(--border); color: #fff; }

.adv-close {
  width: 30px; height: 30px; border-radius: 50%;
  background: var(--bg-input); border: none;
  color: var(--text-secondary); cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  transition: background .15s;
}
.adv-close:hover { background: var(--border); color: #fff; }

.adv-subtitle {
  font-size: 13px; color: var(--text-secondary);
  margin-top: -4px;
}

.adv-field { display: flex; flex-direction: column; gap: 6px; }
.adv-label {
  font-size: 12px; font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase; letter-spacing: .4px;
}

.adv-input-wrap {
  display: flex; align-items: center; gap: 8px;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 0 14px;
}
.adv-input {
  flex: 1;
  background: transparent; border: none; outline: none;
  font-size: 20px; font-weight: 600;
  color: var(--text-primary);
  font-family: inherit;
  padding: 14px 0;
  font-variant-numeric: tabular-nums;
  -moz-appearance: textfield;
  appearance: textfield;
}
.adv-input::-webkit-inner-spin-button,
.adv-input::-webkit-outer-spin-button { -webkit-appearance: none; appearance: none; }
.adv-currency {
  font-size: 18px; font-weight: 600;
  color: var(--text-secondary);
}

.adv-save {
  width: 100%;
  padding: 16px;
  border-radius: 14px;
  background: var(--bg-input);
  color: var(--accent-blue);
  font-size: 16px; font-weight: 600;
  border: 1px solid var(--border);
  cursor: pointer;
  transition: opacity .15s, transform .1s;
}
.adv-save:active { transform: scale(0.98); }
.adv-save:disabled { opacity: 0.4; cursor: default; }
</style>
