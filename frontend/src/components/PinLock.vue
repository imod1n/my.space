<template>
  <div class="pin-overlay">

    <!-- Фоновый градиент -->
    <div class="pin-bg-glow" />

    <div class="pin-container">

      <!-- Иконка-замок -->
      <div class="pin-icon-wrap">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
          <path d="M7 11V7a5 5 0 0 1 10 0v4" stroke="rgba(255,255,255,0.9)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          <rect x="3" y="11" width="18" height="11" rx="3" fill="rgba(255,255,255,0.08)" stroke="rgba(255,255,255,0.25)" stroke-width="1.5"/>
          <circle cx="12" cy="16.5" r="1.5" fill="rgba(255,255,255,0.7)"/>
        </svg>
      </div>

      <!-- Заголовок -->
      <div class="pin-header">
        <p class="pin-title">Введите код доступа</p>
      </div>

      <!-- Индикаторы -->
      <div class="pin-dots" :class="{ shake: shaking }">
        <div
          v-for="i in 4"
          :key="i"
          class="pin-dot"
          :class="{
            filled: pin.length >= i,
            error: shaking
          }"
        />
      </div>

      <!-- Клавиатура -->
      <div class="pin-keyboard">
        <button
          v-for="key in keys"
          :key="key"
          class="pin-key"
          :class="{ ghost: key === '' }"
          @click="handleKey(key)"
        >
          <template v-if="key === 'del'">
            <svg width="20" height="15" viewBox="0 0 20 15" fill="none">
              <path d="M7 1H18C18.5523 1 19 1.44772 19 2V13C19 13.5523 18.5523 14 18 14H7L1 7.5L7 1Z" stroke="rgba(255,255,255,0.7)" stroke-width="1.4" stroke-linejoin="round"/>
              <path d="M11.5 5L8.5 10M8.5 5L11.5 10" stroke="rgba(255,255,255,0.7)" stroke-width="1.4" stroke-linecap="round"/>
            </svg>
          </template>
          <template v-else>{{ key }}</template>
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['unlocked'])

const PIN_HASH = import.meta.env.VITE_PIN_HASH

const pin = ref('')
const shaking = ref(false)

const keys = ['1','2','3','4','5','6','7','8','9','','0','del']

async function sha256(str) {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(str))
  return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('')
}

async function handleKey(key) {
  if (shaking.value) return

  if (key === 'del') {
    pin.value = pin.value.slice(0, -1)
    return
  }

  if (key === '' || pin.value.length >= 4) return

  pin.value += key

  if (pin.value.length === 4) {
    const hash = await sha256(pin.value)
    if (hash === PIN_HASH) {
      emit('unlocked')
    } else {
      shaking.value = true
      setTimeout(() => {
        shaking.value = false
        pin.value = ''
      }, 600)
    }
  }
}
</script>

<style scoped>
.pin-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: #0d0d0f;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

/* Мягкое свечение в центре */
.pin-bg-glow {
  position: absolute;
  top: 30%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(48, 209, 88, 0.06) 0%, transparent 70%);
  pointer-events: none;
}

.pin-container {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 36px;
  width: 100%;
  max-width: 300px;
  padding: 0 16px;
}

/* Иконка */
.pin-icon-wrap {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
}

/* Заголовок */
.pin-header {
  margin-top: -12px;
  text-align: center;
}

.pin-title {
  font-size: 16px;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.55);
  margin: 0;
  letter-spacing: 0.1px;
}

/* Dots */
.pin-dots {
  display: flex;
  gap: 18px;
}

.pin-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 1.5px solid rgba(255, 255, 255, 0.3);
  background: transparent;
  transition: background 0.2s, border-color 0.2s, box-shadow 0.2s, transform 0.15s;
}

.pin-dot.filled {
  background: #ffffff;
  border-color: #ffffff;
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.35);
  transform: scale(1.1);
}

.pin-dot.error {
  background: #ff453a;
  border-color: #ff453a;
  box-shadow: 0 0 10px rgba(255, 69, 58, 0.5);
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  18%       { transform: translateX(-9px); }
  36%       { transform: translateX(9px); }
  54%       { transform: translateX(-6px); }
  72%       { transform: translateX(6px); }
  90%       { transform: translateX(-3px); }
}

.shake { animation: shake 0.55s cubic-bezier(.36,.07,.19,.97); }

/* Keyboard */
.pin-keyboard {
  display: grid;
  grid-template-columns: repeat(3, 76px);
  gap: 12px;
}

.pin-key {
  width: 76px;
  height: 76px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.07);
  background: rgba(255, 255, 255, 0.065);
  color: rgba(255, 255, 255, 0.92);
  font-size: 28px;
  font-weight: 300;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.12s, transform 0.1s, border-color 0.12s;
  -webkit-tap-highlight-color: transparent;
  user-select: none;
  letter-spacing: -0.5px;
}

.pin-key:active {
  background: rgba(255, 255, 255, 0.18);
  border-color: rgba(255, 255, 255, 0.15);
  transform: scale(0.94);
}

.pin-key.ghost {
  visibility: hidden;
  pointer-events: none;
}
</style>
