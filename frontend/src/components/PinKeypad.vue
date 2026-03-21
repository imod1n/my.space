<template>
  <div class="pk-root">
  <!-- Индикаторы -->
  <div class="pk-dots" :class="{ shake: shaking }">
    <div
      v-for="i in 4" :key="i"
      class="pk-dot"
      :class="{ filled: pin.length >= i, error: shaking }"
    />
  </div>

  <!-- Клавиатура -->
  <div class="pk-keyboard">
    <button
      v-for="(key, idx) in keys" :key="idx"
      class="pk-key"
      :class="{ ghost: key === '' }"
      :disabled="disabled"
      @click="handleKey(key)"
    >
      <template v-if="key === 'del'">
        <span class="mdi mdi-backspace-outline" style="font-size:22px;color:rgba(255,255,255,0.7)"></span>
      </template>
      <template v-else-if="key !== '' && key !== 'extra'">{{ key }}</template>
      <template v-else-if="key === 'extra'">
        <slot name="extra-key" />
      </template>
    </button>
  </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  // '' = ghost (невидимая), 'extra' = показывает слот #extra-key
  extraKey: { type: String, default: '' },
  disabled: { type: Boolean, default: false }
})

const emit = defineEmits(['complete', 'extra-key'])

const pin = ref('')
const shaking = ref(false)

const keys = computed(() => [
  '1', '2', '3',
  '4', '5', '6',
  '7', '8', '9',
  props.extraKey, '0', 'del'
])

async function sha256(str) {
  if (crypto.subtle) {
    const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(str))
    return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('')
  }
  // Fallback для non-HTTPS (локальная сеть без TLS)
  return sha256Fallback(str)
}

function sha256Fallback(str) {
  function rightRotate(value, amount) {
    return (value >>> amount) | (value << (32 - amount))
  }
  const maxWord = Math.pow(2, 32)
  let result = ''
  const words = []
  const asciiBitLength = str.length * 8

  let hash = []
  const k = []
  let primeCounter = 0

  const isComposite = {}
  for (let candidate = 2; primeCounter < 64; candidate++) {
    if (!isComposite[candidate]) {
      for (let i = 0; i < 313; i += candidate) isComposite[i] = candidate
      hash[primeCounter] = (Math.pow(candidate, 0.5) * maxWord) | 0
      k[primeCounter++] = (Math.pow(candidate, 1 / 3) * maxWord) | 0
    }
  }

  str += '\x80'
  while (str.length % 64 - 56) str += '\x00'
  for (let i = 0; i < str.length; i++) {
    const j = str.charCodeAt(i)
    if (j >> 8) return '' // non-ASCII — не поддерживается в fallback
    words[i >> 2] |= j << ((3 - i) % 4) * 8
  }
  words[words.length] = (asciiBitLength / maxWord) | 0
  words[words.length] = asciiBitLength

  for (let j = 0; j < words.length;) {
    const w = words.slice(j, (j += 16))
    const oldHash = hash.slice(0)
    for (let i = 0; i < 64; i++) {
      const w15 = w[i - 15]
      const w2 = w[i - 2]
      const a = hash[0], e = hash[4]
      const temp1 = hash[7] +
        (rightRotate(e, 6) ^ rightRotate(e, 11) ^ rightRotate(e, 25)) +
        ((e & hash[5]) ^ (~e & hash[6])) +
        k[i] + (w[i] = i < 16 ? w[i] : (
          w[i - 16] +
          (rightRotate(w15, 7) ^ rightRotate(w15, 18) ^ (w15 >>> 3)) +
          w[i - 7] +
          (rightRotate(w2, 17) ^ rightRotate(w2, 19) ^ (w2 >>> 10))
        ) | 0)
      const temp2 = (rightRotate(a, 2) ^ rightRotate(a, 13) ^ rightRotate(a, 22)) +
        ((a & hash[1]) ^ (a & hash[2]) ^ (hash[1] & hash[2]))
      hash = [temp1 + temp2, a, hash[1], hash[2], (hash[3] + temp1) | 0, hash[4], hash[5], hash[6]]
    }
    for (let i = 0; i < 8; i++) hash[i] = (hash[i] + oldHash[i]) | 0
  }
  for (let i = 0; i < 8; i++) {
    for (let j = 3; j + 1; j--) {
      const b = (hash[i] >> (j * 8)) & 255
      result += (b < 16 ? '0' : '') + b.toString(16)
    }
  }
  return result
}

async function handleKey(key) {
  if (shaking.value || props.disabled) return

  if (key === 'del') {
    pin.value = pin.value.slice(0, -1)
    return
  }
  if (key === 'extra') {
    emit('extra-key')
    return
  }
  if (key === '') return
  if (pin.value.length >= 4) return

  pin.value += key

  if (pin.value.length === 4) {
    const hash = await sha256(pin.value)
    emit('complete', hash)
  }
}

function shake() {
  shaking.value = true
  setTimeout(() => {
    shaking.value = false
    pin.value = ''
  }, 650)
}

function reset() {
  pin.value = ''
  shaking.value = false
}

defineExpose({ shake, reset })
</script>

<style scoped>
.pk-root { display: contents; }

/* PIN Dots */
.pk-dots {
  display: flex;
  gap: 18px;
}

.pk-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 1.5px solid rgba(255, 255, 255, 0.3);
  background: transparent;
  transition: background 0.2s, border-color 0.2s, box-shadow 0.2s, transform 0.15s;
}

.pk-dot.filled {
  background: #ffffff;
  border-color: #ffffff;
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.35);
  transform: scale(1.1);
}

.pk-dot.error {
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

.shake { animation: shake 0.55s cubic-bezier(.36, .07, .19, .97); }

/* Keyboard */
.pk-keyboard {
  display: grid;
  grid-template-columns: repeat(3, 76px);
  gap: 12px;
}

.pk-key {
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
  touch-action: none;
  user-select: none;
  letter-spacing: -0.5px;
}

.pk-key:active {
  background: rgba(255, 255, 255, 0.18);
  border-color: rgba(255, 255, 255, 0.15);
  transform: scale(0.94);
}

.pk-key.ghost {
  visibility: hidden;
  pointer-events: none;
}

.pk-key:disabled {
  opacity: 0.4;
  cursor: default;
}
</style>
