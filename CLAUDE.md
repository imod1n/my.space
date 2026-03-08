# 🤖 CLAUDE.md — Всё о проекте "Коммуналка семьи"

> Этот файл — полная база знаний проекта для Claude.  
> Читать перед любыми изменениями в коде.

---

## 📋 Что это за проект

**PWA-приложение** для семейного учёта коммунальных платежей.  
Семья устанавливает его на iPhone как приложение (Add to Home Screen), вводит платежи, смотрит статистику и графики по месяцам.

**Ключевые качества:**
- 📱 Работает как нативное iOS-приложение (PWA standalone)
- 🌙 Тёмная тема iOS (`#111111` фон, `#30d158` акцент)
- 📴 Оффлайн-поддержка через Service Worker
- 💰 Бесплатный хостинг навсегда (GitHub Pages + Render free tier + MongoDB Atlas M0)

---

## 🚀 Продакшен — живые URL

| Сервис | URL |
|--------|-----|
| **Frontend** | https://imod1n.github.io/pwa-kommunalka/ |
| **Backend API** | https://kommunalka-api.onrender.com |
| **API Docs** | https://kommunalka-api.onrender.com/docs |
| **Healthcheck** | https://kommunalka-api.onrender.com/health |

---

## 🏗️ Архитектура

```
┌──────────────────────────────────────────────────────────────┐
│  FRONTEND (Vue 3)           BACKEND (FastAPI)                 │
│  GitHub Pages               Render Frankfurt                  │
│                                                               │
│  imod1n.github.io    →      kommunalka-api.onrender.com  →   │
│  Vue 3 + Pinia              Motor async              MongoDB  │
│  Chart.js                   Pydantic v2              Atlas M0 │
│  vite-plugin-pwa            Python 3.11.8            Frankfurt│
│  CI/CD: GitHub Actions                                        │
└──────────────────────────────────────────────────────────────┘
```

---

## ☁️ Инфраструктура продакшена

### GitHub
- **Репозиторий:** `imod1n/pwa-kommunalka`
- **Ветка:** `master` (не main — важно!)
- **GitHub Pages:** включён, Source = **GitHub Actions**
- **Secrets:**
  - `VITE_API_URL = https://kommunalka-api.onrender.com`
  - `VITE_PIN_HASH` = SHA-256 хеш 4-значного PIN-кода (см. раздел ниже)
- **CI/CD:** `.github/workflows/deploy.yml` — триггер на push в `master`, Node 20, `npm ci`

### Render
- **Сервис:** `kommunalka-api` (Web Service, Free)
- **Регион:** Frankfurt (EU Central)
- **Runtime:** Python 3.11.8 (зафиксирован через `backend/.python-version`)
- **Конфиг:** `render.yaml` в корне репозитория (без Root Directory)
- **Build Command:** `pip install -r backend/requirements.txt`
- **Start Command:** `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
- **Env vars на Render:**
  - `MONGO_URL` = `mongodb+srv://kommunalka:<pass>@main1.brpynju.mongodb.net/kommunalka?retryWrites=true&w=majority&appName=Main1`
  - `DB_NAME` = `kommunalka`
- ⚠️ Free tier засыпает через 15 мин → пингуется автоматически через `.github/workflows/keepalive.yml` каждые 10 мин

### MongoDB Atlas
- **Провайдер:** AWS / Frankfurt
- **Кластер:** M0 Free (`main1.brpynju.mongodb.net`)
- **База данных:** `kommunalka`
- **Пользователь:** `kommunalka`
- **Network Access:** `0.0.0.0/0` (Allow from anywhere)

---

## 📁 Структура файлов

```
pwa-kommunalka/
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── style.css
│   │   ├── components/
│   │   │   ├── PaymentForm.vue        # Форма добавления платежа
│   │   │   ├── StatsTable.vue         # По категориям / по объектам (по умолчанию)
│   │   │   ├── MonthlyChart.vue       # Chart.js: 3 режима (Итого / По категориям / По годам)
│   │   │   ├── ImportExport.vue       # Импорт/Экспорт CSV + очистка базы
│   │   │   └── PinLock.vue            # Экран блокировки PIN-кода
│   │   ├── views/
│   │   │   └── Dashboard.vue          # Главный экран
│   │   ├── stores/
│   │   │   └── payments.js            # Pinia store
│   │   └── api/
│   │       └── payments.js            # Axios клиент
│   ├── public/
│   │   ├── icon-192.png               # PWA иконка (нужно создать!)
│   │   ├── icon-512.png               # PWA иконка большая
│   │   └── version.json               # генерируется CI при каждом деплое (git hash + timestamp)
│   ├── vite.config.js                 # base: '/pwa-kommunalka/', PWA плагин
│   ├── postcss.config.js              # module.exports (не ES module!)
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI + CORS + lifespan
│   │   ├── models.py                  # Pydantic схемы
│   │   ├── crud.py                    # Motor async операции
│   │   └── database.py                # Подключение + индексы
│   ├── requirements.txt
│   └── .python-version                # 3.11.8 — критично для Render!
│
├── .github/workflows/
│   ├── deploy.yml                     # branches: [master] ← важно!
│   └── keepalive.yml                  # пинг /health каждые 10 мин (Render не засыпает)
│
├── render.yaml                        # Render deploy config (без rootDirectory)
├── docker-compose.yml                 # mongo:7.0 для локальной разработки
└── CLAUDE.md
```

---

## 🎨 Дизайн-система

### Цветовая палитра
```css
--bg-primary:    #111111
--bg-secondary:  #1c1c1e
--bg-card:       #2c2c2e
--bg-input:      #3a3a3c
--text-primary:  #ffffff
--text-secondary:#8e8e93
--accent-green:  #30d158   /* кнопки, суммы */
--accent-blue:   #0a84ff   /* вкладки */
--accent-orange: #ff9f0a   /* Газ */
--accent-red:    #ff453a   /* ошибки, рост */
--accent-yellow: #ffd60a   /* Электричество */
--accent-purple: #bf5af2   /* Интернет */
--border:        #38383a
```

---

## ⚙️ Технический стек

### Frontend
| Пакет | Версия |
|-------|--------|
| Vue 3 | ^3.4.0 |
| Pinia | ^2.1.7 |
| Axios | ^1.6.0 |
| Chart.js | ^4.4.0 |
| vue-chartjs | ^5.2.0 |
| vue-router | ^4.3.0 |
| Vite | ^5.0.0 |
| vite-plugin-pwa | ^0.19.0 |
| Tailwind CSS | ^3.4.0 |

### Backend
| Пакет | Версия |
|-------|--------|
| fastapi | 0.110.0 |
| motor | 3.3.2 |
| pymongo | 4.6.3 (явно!) |
| pydantic | 2.7.0 |
| uvicorn[standard] | 0.29.0 |
| python-dateutil | 2.9.0 |
| python-dotenv | 1.0.0 |

---

## 🔌 API Endpoints

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/api/payments` | Добавить платёж |
| GET | `/api/payments?limit=200` | Список платежей |
| PUT | `/api/payments/{id}` | Редактировать платёж |
| DELETE | `/api/payments/{id}` | Удалить по ObjectId |
| DELETE | `/api/payments/all` | Удалить все платежи (очистка базы) |
| GET | `/api/stats/{month}` | Статистика за месяц (YYYY-MM) |
| GET | `/api/stats-history?months=6` | История для графика (используется с months=6 и months=36) |
| GET | `/health` | Healthcheck для Render/cron |

> ⚠️ Маршрут `DELETE /api/payments/all` должен быть объявлен в `main.py` **до** `DELETE /api/payments/{id}`, иначе FastAPI будет пытаться трактовать `all` как ObjectId.

---

## 📂 Категории и объекты

```python
class Category(str, Enum):
    communal    = "Коммунальные"   # 🏘️ #0a84ff
    electricity = "Электричество"  # ⚡ #ffd60a
    internet    = "Интернет"       # 🌐 #bf5af2
    tv          = "Телевидение"    # 📺 #30d158
    trash       = "Мусор"          # 🗑️ #636366
    membership  = "Членские"       # 🪪 #ff9f0a
    snow        = "Уборка снега"   # ❄️ #5ac8fa
    other       = "Прочее"         # 📎 #8e8e93

class ObjectName(str, Enum):
    flat1   = "Квартира 1"
    flat2   = "Квартира 2"
    country = "Загородный дом"
    beach   = "Пляжный домик"
```

---

## 🔧 Переменные окружения

### Frontend
```env
# локально (.env.local)
VITE_API_URL=http://localhost:8000
# VITE_PIN_HASH не задаётся локально — PIN экран автоматически отключается

# продакшен — GitHub Secrets, подставляются CI/CD автоматически
VITE_API_URL=https://kommunalka-api.onrender.com
VITE_PIN_HASH=<sha256-хеш-пин-кода>
```

### Backend
```env
# локально (.env)
MONGO_URL=mongodb://localhost:27017
DB_NAME=kommunalka
# продакшен — Render Environment Variables
MONGO_URL=mongodb+srv://kommunalka:<pass>@main1.brpynju.mongodb.net/kommunalka?retryWrites=true&w=majority&appName=Main1
DB_NAME=kommunalka
```

---

## 🚀 Локальная разработка

```bash
# MongoDB
docker-compose up -d          # mongo:7.0 на порту 27017

# Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm run dev                   # → http://localhost:5173/pwa-kommunalka/

# Деплой (автоматически)
git push origin master        # → GitHub Actions → GitHub Pages
```

---

## ⚠️ Критичные нюансы

1. **Ветка `master`** — в `deploy.yml` прописано `branches: [master]`, не main
2. **`backend/.python-version = 3.11.8`** — без этого Render берёт Python 3.14, `pydantic-core` не собирается (нет prebuilt wheel, нужен Rust)
3. **`pymongo==4.6.3`** явно в `requirements.txt` — motor тянет несовместимую версию без явной фиксации
4. **MongoDB Atlas, не Render** — MongoDB нельзя запустить как Web Service на Render (ждёт HTTP, убивает по таймауту)
5. **`postcss.config.js`** — `module.exports`, не `export default`
6. **`font-size: 16px` в input** — иначе iPhone зумит форму
7. **`base: '/pwa-kommunalka/'`** в `vite.config.js` — совпадает с именем репозитория
8. **CORS** — настроен на `https://*.github.io` и `https://imod1n.github.io`
9. **Render засыпает** через 15 мин → пингуется автоматически через `keepalive.yml` (GitHub Actions, cron `*/10 * * * *`). Если репозиторий долго неактивен (>60 дней без пушей), GitHub может отключить scheduled workflow — нужно зайти в Actions и нажать "Enable workflow".
10. **PWA иконки** — нужно создать `icon-192.png` и `icon-512.png` в `frontend/public/` (папка сейчас пустая!)
11. **PIN-блокировка** — работает только в продакшене (если `VITE_PIN_HASH` задан). Локально без этого секрета экран блокировки не появляется. Логика: холодный старт всегда блокирует; фон > 5 мин → повторная блокировка; фон < 5 мин → не блокирует.
12. **Автообновление кэша PWA** — многоуровневое. SW-уровень: `skipWaiting: true`, `clientsClaim: true`, `controllerchange` → `reload()`, `reg.update()` каждые 60 сек и при возврате из фона. iOS-уровень (обход бага Safari с кэшем SW): `version.json` polling — CI генерирует `frontend/public/version.json` с git hash, `App.vue` проверяет его каждые 2 мин через `fetch` с `cache: 'no-store'`, при смене хеша → `reload()`. **Не убирать эти настройки!**
13. **Шапка на iOS PWA** — `padding-top: calc(env(safe-area-inset-top, 0px) + 12px)` чтобы не налезала на статус-бар в standalone режиме.

---

## 🛣️ Возможные улучшения

- [ ] PWA иконки (сейчас заглушки)
- [x] Пинг Render — реализовано (`keepalive.yml`, GitHub Actions cron каждые 10 мин)
- [x] Авторизация по PIN-коду — реализовано (PinLock.vue, VITE_PIN_HASH в GitHub Secrets)
- [ ] Push-уведомления
- [x] Редактирование платежей — реализовано (модалка в StatsTable)
- [x] Несколько объектов — реализовано (4 объекта, вкладка «По объектам»)
- [x] Экспорт/Импорт CSV — реализовано (ImportExport.vue, вкладка «Данные»)
- [x] Очистка базы — реализовано (DELETE /api/payments/all + кнопка с двойным подтверждением)
- [x] График "По годам" — реализовано (grouped bars, скролл на мобиле, клик → переход на период)
- [x] Калькулятор периодов — реализовано (bottom sheet, диапазон С/По, сумма + среднее + детализация по объектам)
- [x] Автообновление iOS PWA — реализовано (version.json polling, обходит баг Safari с кэшем SW)

---

## 🔐 PIN-блокировка — как сменить код

### Когда запрашивается PIN
- **Холодный старт** — при каждом открытии вкладки/PWA (sessionStorage пуст)
- **Возврат из фона** — если приложение было свёрнуто/экран заблокирован **более 5 минут**
- **Не запрашивается** — при навигации внутри приложения и коротком сворачивании (< 5 мин)

### Как сменить PIN

1. Сгенерируй SHA-256 хеш нового 4-значного кода в терминале:
```bash
node -e "const crypto=require('crypto'); console.log(crypto.createHash('sha256').update('НОВЫЙ_ПИН').digest('hex'))"
```

2. Открой **github.com/imod1n/pwa-kommunalka** → Settings → Secrets and variables → Actions

3. Найди секрет `VITE_PIN_HASH` → **Update** → вставь новый хеш → **Save**

4. Запусти деплой вручную:
   - Actions → Deploy PWA to GitHub Pages → **Run workflow** → Run workflow
   - Либо сделай любой push в `master`

5. После деплоя (~2 мин) новый PIN активен. Старый перестаёт работать.

### Архитектура безопасности
- PIN хранится **только как SHA-256 хеш** в GitHub Secret — в исходном коде его нет
- В скомпилированном JS-бандле будет хеш, но не сам PIN
- Защищает от **случайного просмотра**, не от целенаправленного взлома (4 цифры = 10 000 комбинаций)
- Для семейного приложения этого уровня достаточно

---

## 🗒️ Ключевые решения интерфейса

- **Вкладка «По объектам»** открывается по умолчанию (`ref('objects')` в StatsTable)
- **Мобильная адаптация таблицы** (`@media max-width: 849px`): скрыта шапка, строки перестраиваются в карточки через `grid-template-areas`
- **Вкладки Dashboard:** «Обзор доски» / «Добавить платеж» / «Данные»
- **Дедупликация импорта:** сравнение по 5 полям (`category + object_name + amount + date + period`), дубликаты подсвечиваются оранжевым и пропускаются
- **CSV-экспорт:** генерируется на фронте, BOM (`\ufeff`) для корректного открытия в Excel
- **Переключатель месяца:** по умолчанию — текущий месяц по дате (`todayPeriod()`); клик по названию месяца сбрасывает на текущий
- **График "По годам":** grouped bar chart, ось X = 12 месяцев, каждый год = датасет; цвета: 2023=синий, 2024=зелёный, 2025=оранжевый, 2026=фиолетовый; на мобиле горизонтальный скролл (`min-width: 1100px`), на десктопе растягивается; клик по бару переключает период в переключателе месяца
- **`store.historyFull`** — отдельная выборка 36 месяцев (`getStatsHistory(36)`) для графика по годам и калькулятора; загружается в `init()` параллельно с остальными данными
- **Калькулятор периодов:** иконка-кнопка в правом верхнем углу герой-карточки; открывает bottom sheet с выбором диапазона «С»/«По» из доступных периодов; показывает сумму, количество месяцев, среднее в месяц и **детализацию по объектам** (суммируется из `store.payments`, без доп. запросов к API); по умолчанию диапазон: -3 месяца от сегодня → текущий месяц

---

*Последнее обновление: 2026-03-08 | Версия: 1.4.0*
