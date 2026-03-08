<template>
  <div class="min-h-screen" style="background: var(--bg-primary)">
    <PinLock v-if="locked" @unlocked="onUnlocked" />
    <Dashboard v-else />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import Dashboard from './views/Dashboard.vue'
import PinLock from './components/PinLock.vue'

const PIN_HASH = import.meta.env.VITE_PIN_HASH
const LOCK_TIMEOUT_MS = 5 * 60 * 1000 // 5 минут в фоне → перезапросить PIN

const locked = ref(false)

function onUnlocked() {
  locked.value = false
  sessionStorage.setItem('pin_unlocked', '1')
  localStorage.removeItem('hidden_at')
}

function handleVisibilityChange() {
  if (document.visibilityState === 'hidden') {
    localStorage.setItem('hidden_at', String(Date.now()))
  } else {
    // Проверяем обновления SW при возврате из фона
    navigator.serviceWorker?.ready.then(reg => reg.update())

    const hiddenAt = Number(localStorage.getItem('hidden_at') || 0)
    if (hiddenAt && Date.now() - hiddenAt > LOCK_TIMEOUT_MS) {
      locked.value = true
      sessionStorage.removeItem('pin_unlocked')
    }
    localStorage.removeItem('hidden_at')
  }
}

// Перезагружаем страницу когда новый SW берёт контроль
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    window.location.reload()
  })
}

let swUpdateInterval = null
let versionInterval = null
let currentVersion = null

async function checkVersion() {
  try {
    const base = import.meta.env.BASE_URL || '/'
    const res = await fetch(`${base}version.json?t=${Date.now()}`, { cache: 'no-store' })
    if (!res.ok) return
    const { v } = await res.json()
    if (!currentVersion) { currentVersion = v; return }
    if (v !== currentVersion) window.location.reload()
  } catch { /* офлайн — пропускаем */ }
}

onMounted(() => {
  // Показываем PIN только если он настроен
  if (PIN_HASH) {
    // Холодный старт: sessionStorage пуст → блокируем
    locked.value = !sessionStorage.getItem('pin_unlocked')
    document.addEventListener('visibilitychange', handleVisibilityChange)
  }

  // Периодически проверяем обновления SW (каждые 60 секунд)
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.ready.then(reg => {
      swUpdateInterval = setInterval(() => reg.update(), 60_000)
    })
  }

  // Проверка версии через version.json каждые 2 минуты (надёжно работает на iOS)
  checkVersion()
  versionInterval = setInterval(checkVersion, 2 * 60_000)
})

onUnmounted(() => {
  document.removeEventListener('visibilitychange', handleVisibilityChange)
  if (swUpdateInterval) clearInterval(swUpdateInterval)
  if (versionInterval) clearInterval(versionInterval)
})
</script>
