<div align="center">

<!-- Replace with actual logo path when available -->
<!-- <img src="./docs/logo.svg" alt="DotACoach.AI" width="180" /> -->

```
  ____        _        ____                 _       _    ___
 |  _ \  ___ | |_ /\  / ___|___   __ _  __| |_    / \  |_ _|
 | | | |/ _ \| __/  \| |   / _ \ / _` |/ _` \ \  / _ \  | |
 | |_| | (_) | || /\ | |__| (_) | (_| | (_| |\ \/ / ___ \ | |
 |____/ \___/ \__\/  \\____\___/ \__,_|\__,_| \__/_/   \_\___|
```

**DotACoach.AI**

*Turn every match into actionable intelligence.*

---

![Build Status](https://img.shields.io/badge/build-passing-brightgreen?style=flat-square&labelColor=0d1117&color=00c853)
![Next.js](https://img.shields.io/badge/Next.js-15-black?style=flat-square&logo=next.js&labelColor=0d1117)
![Django](https://img.shields.io/badge/Django-5.x-092e20?style=flat-square&logo=django&labelColor=0d1117&color=092e20)
![Python](https://img.shields.io/badge/Python-3.12-3776ab?style=flat-square&logo=python&labelColor=0d1117)
![OpenDota](https://img.shields.io/badge/OpenDota-API-ff6f00?style=flat-square&labelColor=0d1117)
![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square&labelColor=0d1117)

</div>

---

## Demo

<div align="center">

<!-- PLACEHOLDER: Replace with actual demo GIF or video link -->
<!-- <img src="./docs/demo.gif" alt="DotACoach.AI Dashboard Demo" width="100%" /> -->

> Demo video / GIF will be placed here.
> Suggested content: Dashboard overview -> Trend charts drill-down -> AI Coach match analysis flow.

</div>

---

## Interface

<div align="center">
<table>
  <tr>
    <td align="center" width="50%">
      <!-- PLACEHOLDER: Screenshot 1 — Landing / Account Input -->
      <!-- <img src="./docs/screenshots/landing.png" alt="Landing Page" /> -->
      <strong>Landing — Account Input</strong>
    </td>
    <td align="center" width="50%">
      <!-- PLACEHOLDER: Screenshot 2 — Dashboard Overview -->
      <!-- <img src="./docs/screenshots/dashboard.png" alt="Dashboard" /> -->
      <strong>Dashboard — Performance Overview</strong>
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <!-- PLACEHOLDER: Screenshot 3 — Trend Charts + Drill-down -->
      <!-- <img src="./docs/screenshots/trends.png" alt="Trend Charts" /> -->
      <strong>Trend Charts — KDA / GPM over time</strong>
    </td>
    <td align="center" width="50%">
      <!-- PLACEHOLDER: Screenshot 4 — AI Coach Match Analysis -->
      <!-- <img src="./docs/screenshots/ai-coach.png" alt="AI Coach" /> -->
      <strong>AI Coach — Per-Match Analysis</strong>
    </td>
  </tr>
</table>
</div>

---

## Core Features

- **Lifetime Hero Statistics** — Global win/loss data pulled from OpenDota's `/heroes` endpoint, not limited to locally stored matches. Always reflects true career performance.
- **Hybrid Data Architecture** — Detailed match telemetry (items, timelines, purchase logs) is stored locally for the 20 most recent matches. Global aggregates are fetched live, keeping storage lean without sacrificing accuracy.
- **AI Coach** — Per-match GPT-powered analysis delivered in a unified chat interface. Follow-up questions retain full match context. No fragmented UI panels, no internal scrollbars.
- **Item Purchase Timings** — Where replay data is available, significant item purchases are timestamped and surfaced directly in the match detail view and AI prompt context.
- **Drill-down Trend Analytics** — Interactive performance charts (GPM, KDA, XPM, Last Hits, Tower Damage) across the player's last 30 matches. Chart points are clickable and navigate to full match detail.
- **Smart Rank Mapping** — Rank tier integers are decoded into human-readable ranks (Herald 1 through Immortal) with estimated MMR ranges derived from game data.
- **Resilient Sync Pipeline** — Background Celery worker with retry logic on OpenDota API calls. Rate-limit failures do not overwrite existing data — the worker exits cleanly and preserves the current state.
- **Strict Dark Mode UI** — Architectural minimal design. No decorative gradients, no emoji, no "bubbly" AI aesthetics. Every element earns its place.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                     Frontend                        │
│   Next.js 15  ·  TypeScript  ·  Vanilla CSS         │
│   Recharts  ·  React Markdown  ·  remark-gfm        │
└────────────────────┬────────────────────────────────┘
                     │ REST API
┌────────────────────▼────────────────────────────────┐
│                     Backend                         │
│   Django 5  ·  Django REST Framework                │
│   Celery  ·  Redis (broker)  ·  PostgreSQL          │
└────────────┬────────────────────┬───────────────────┘
             │                    │
┌────────────▼─────────┐ ┌───────▼────────────────────┐
│   OpenDota API       │ │   AI Engine                │
│   /players/{id}      │ │   OpenAI GPT-4o            │
│   /players/{id}/wl   │ │   Structured match prompts │
│   /players/{id}/heroes│ │   Conversational context  │
│   /matches/{id}      │ └────────────────────────────┘
└──────────────────────┘
```

### Tech Stack

| Layer | Technology |
|---|---|
| Frontend Framework | Next.js 15 (App Router) |
| Language | TypeScript |
| Styling | Vanilla CSS (custom design system) |
| Charts | Recharts |
| Backend Framework | Django 5 + Django REST Framework |
| Task Queue | Celery + Redis |
| Database | PostgreSQL |
| Data Source | OpenDota API (free, no key required) |
| AI Engine | OpenAI GPT-4o |
| Deployment-ready | Docker-composable |

---

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL
- Redis
- OpenAI API Key

### 1. Clone the repository

```bash
git clone https://github.com/Ataniyaz228/dota2-ai-coach.git
cd dota2-ai-coach
```

### 2. Backend setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux / macOS

pip install -r requirements.txt
```

Copy the environment file and fill in your values:

```bash
cp .env.example .env
```

```env
DATABASE_URL=postgres://user:password@localhost:5432/dota2coach
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=sk-...
SECRET_KEY=your-django-secret-key
DEBUG=True
```

Apply migrations and start the server:

```bash
python manage.py migrate
python manage.py runserver
```

Start the background worker (separate terminal):

```bash
celery -A config worker -l info --pool=solo
```

### 3. Frontend setup

```bash
cd frontend
npm install
```

```bash
cp .env.local.example .env.local
```

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

```bash
npm run dev
```

> The frontend will be available at `http://localhost:3000`. Enter any public Dota 2 account ID on the landing page to begin synchronization.

---

## Data Flow

```
User enters Account ID
        |
        v
POST /api/v1/profile/link
        |
        v
Celery task: sync_player_data(account_id)
  |
  |-- _sync_profile()     -> /players/{id}  + /players/{id}/wl
  |-- _sync_matches()     -> /players/{id}/matches + /matches/{id} (last 20 detail)
  |-- _update_hero_stats() -> /players/{id}/heroes  [with retry + rate-limit guard]
        |
        v
PostgreSQL: Player, Match, PlayerMatch, PlayerHeroStats
        |
        v
Dashboard API serves merged lifetime + recent data
```

---

## Architectural Notes

> **On data storage strategy:** Only the 20 most recent matches are stored with full detail (purchase logs, timelines, ability upgrades). Global hero statistics (career games, wins) are fetched from OpenDota's aggregated endpoint and stored as a flat summary. This avoids unbounded database growth while preserving analytical accuracy.

> **On rate limiting:** OpenDota enforces soft rate limits on free-tier API access. The sync pipeline introduces deliberate delays between match detail requests and implements a 2-attempt retry with a 3-second backoff specifically for the `/heroes` endpoint, which is called last in the pipeline and most susceptible to exhausted quotas.

> **On AI context:** The GPT prompt receives structured match data including: hero, KDA, GPM, XPM, item build with purchase timings (where available), laning role, net worth, gold advantage timeline, and the player's lifetime hero statistics. This allows the model to contextualize individual match performance against historical baselines.

---

## License

MIT License. See [LICENSE](./LICENSE) for details.

---

<div align="center">

Built with precision. No filler, no fluff.

</div>

---
---

<!-- ============================================================ -->
<!-- RUSSIAN VERSION / РУССКАЯ ВЕРСИЯ -->
<!-- ============================================================ -->

<div align="center">

```
  ____        _        ____                 _       _    ___
 |  _ \  ___ | |_ /\  / ___|___   __ _  __| |_    / \  |_ _|
 | | | |/ _ \| __/  \| |   / _ \ / _` |/ _` \ \  / _ \  | |
 | |_| | (_) | || /\ | |__| (_) | (_| | (_| |\ \/ / ___ \ | |
 |____/ \___/ \__\/  \\____\___/ \__,_|\__,_| \__/_/   \_\___|
```

**DotACoach.AI**

*Каждый матч — источник конкретных действий.*

---

![Build Status](https://img.shields.io/badge/сборка-успешна-brightgreen?style=flat-square&labelColor=0d1117&color=00c853)
![Next.js](https://img.shields.io/badge/Next.js-15-black?style=flat-square&logo=next.js&labelColor=0d1117)
![Django](https://img.shields.io/badge/Django-5.x-092e20?style=flat-square&logo=django&labelColor=0d1117&color=092e20)
![Python](https://img.shields.io/badge/Python-3.12-3776ab?style=flat-square&logo=python&labelColor=0d1117)
![OpenDota](https://img.shields.io/badge/OpenDota-API-ff6f00?style=flat-square&labelColor=0d1117)
![License](https://img.shields.io/badge/лицензия-MIT-blue?style=flat-square&labelColor=0d1117)

</div>

---

## Демонстрация

<div align="center">

<!-- PLACEHOLDER: Замените на реальный GIF или ссылку на видео -->
<!-- <img src="./docs/demo.gif" alt="Демо дашборда DotACoach.AI" width="100%" /> -->

> Демо-видео / GIF будет размещено здесь.
> Рекомендуемый контент: обзор дашборда -> детализация трендов -> анализ матча через AI Coach.

</div>

---

## Интерфейс

<div align="center">
<table>
  <tr>
    <td align="center" width="50%">
      <!-- PLACEHOLDER: Скриншот 1 — Главная страница / ввод аккаунта -->
      <!-- <img src="./docs/screenshots/landing.png" alt="Главная страница" /> -->
      <strong>Главная — Ввод аккаунта</strong>
    </td>
    <td align="center" width="50%">
      <!-- PLACEHOLDER: Скриншот 2 — Обзор дашборда -->
      <!-- <img src="./docs/screenshots/dashboard.png" alt="Дашборд" /> -->
      <strong>Дашборд — Общая статистика</strong>
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <!-- PLACEHOLDER: Скриншот 3 — Тренды и детализация -->
      <!-- <img src="./docs/screenshots/trends.png" alt="Графики трендов" /> -->
      <strong>Тренды — KDA / GPM по матчам</strong>
    </td>
    <td align="center" width="50%">
      <!-- PLACEHOLDER: Скриншот 4 — AI Coach, анализ матча -->
      <!-- <img src="./docs/screenshots/ai-coach.png" alt="AI Coach" /> -->
      <strong>AI Coach — Анализ отдельного матча</strong>
    </td>
  </tr>
</table>
</div>

---

## Ключевые возможности

- **Статистика героев за всё время** — Глобальные данные о победах и поражениях берутся из эндпоинта `/heroes` OpenDota, а не только из локально сохранённых матчей. Всегда отражает реальную карьерную статистику.
- **Гибридная архитектура данных** — Детальное телеметрие матча (предметы, таймлайны, логи покупок) хранится локально только для 20 последних матчей. Глобальные агрегаты запрашиваются в режиме реального времени — хранилище остаётся компактным, точность не страдает.
- **AI Coach** — Анализ каждого матча через GPT-4o в едином интерфейсе чата. Уточняющие вопросы сохраняют полный контекст матча. Никаких разрозненных панелей, никаких вложенных полос прокрутки.
- **Тайминги покупки предметов** — Там, где есть данные реплея, значимые покупки предметов отмечены временными метками прямо в детализации матча и контексте AI-промпта.
- **Drill-down аналитика трендов** — Интерактивные графики производительности (GPM, KDA, XPM, Last Hits, урон по строениям) по последним 30 матчам игрока. Точки на графике кликабельны и ведут к полной детализации матча.
- **Умная расшифровка ранга** — Числовые значения rank_tier декодируются в читаемые ранги (от Herald 1 до Immortal) с расчётом диапазона MMR по данным игры.
- **Устойчивый конвейер синхронизации** — Фоновый воркер Celery с логикой повторных попыток при обращении к API OpenDota. Ошибки rate-limit не перезаписывают существующие данные — воркер корректно завершает работу, сохраняя текущее состояние.
- **Строгий тёмный интерфейс** — Архитектурный минималистичный дизайн. Никаких декоративных градиентов, никаких эмодзи, никакой "пузырчатой" AI-эстетики. Каждый элемент оправдывает своё присутствие.

---

## Архитектура

```
┌─────────────────────────────────────────────────────┐
│                     Фронтенд                        │
│   Next.js 15  ·  TypeScript  ·  Vanilla CSS         │
│   Recharts  ·  React Markdown  ·  remark-gfm        │
└────────────────────┬────────────────────────────────┘
                     │ REST API
┌────────────────────▼────────────────────────────────┐
│                     Бэкенд                          │
│   Django 5  ·  Django REST Framework                │
│   Celery  ·  Redis (брокер)  ·  PostgreSQL          │
└────────────┬────────────────────┬───────────────────┘
             │                    │
┌────────────▼─────────┐ ┌───────▼────────────────────┐
│   OpenDota API       │ │   AI-движок                │
│   /players/{id}      │ │   OpenAI GPT-4o            │
│   /players/{id}/wl   │ │   Структурированные промпты│
│   /players/{id}/heroes│ │   Контекст разговора      │
│   /matches/{id}      │ └────────────────────────────┘
└──────────────────────┘
```

### Стек технологий

| Слой | Технология |
|---|---|
| Фреймворк фронтенда | Next.js 15 (App Router) |
| Язык | TypeScript |
| Стилизация | Vanilla CSS (собственная дизайн-система) |
| Графики | Recharts |
| Фреймворк бэкенда | Django 5 + Django REST Framework |
| Очередь задач | Celery + Redis |
| База данных | PostgreSQL |
| Источник данных | OpenDota API (бесплатно, ключ не нужен) |
| AI-движок | OpenAI GPT-4o |
| Готов к развёртыванию | Docker-composable |

---

## Быстрый старт

### Требования

- Python 3.12+
- Node.js 20+
- PostgreSQL
- Redis
- Ключ API OpenAI

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/Ataniyaz228/dota2-ai-coach.git
cd dota2-ai-coach
```

### 2. Настройка бэкенда

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux / macOS

pip install -r requirements.txt
```

Скопируйте файл окружения и заполните значения:

```bash
cp .env.example .env
```

```env
DATABASE_URL=postgres://user:password@localhost:5432/dota2coach
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=sk-...
SECRET_KEY=ваш-django-секретный-ключ
DEBUG=True
```

Примените миграции и запустите сервер:

```bash
python manage.py migrate
python manage.py runserver
```

Запустите фоновый воркер (отдельный терминал):

```bash
celery -A config worker -l info --pool=solo
```

### 3. Настройка фронтенда

```bash
cd frontend
npm install
```

```bash
cp .env.local.example .env.local
```

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

```bash
npm run dev
```

> Фронтенд будет доступен по адресу `http://localhost:3000`. Введите любой публичный ID аккаунта Dota 2 на главной странице, чтобы начать синхронизацию.

---

## Поток данных

```
Пользователь вводит Account ID
        |
        v
POST /api/v1/profile/link
        |
        v
Celery-задача: sync_player_data(account_id)
  |
  |-- _sync_profile()     -> /players/{id}  + /players/{id}/wl
  |-- _sync_matches()     -> /players/{id}/matches + /matches/{id} (детализация последних 20)
  |-- _update_hero_stats() -> /players/{id}/heroes  [с retry + защитой от rate-limit]
        |
        v
PostgreSQL: Player, Match, PlayerMatch, PlayerHeroStats
        |
        v
Dashboard API предоставляет объединённые данные (Lifetime + Recent)
```

---

## Архитектурные примечания

> **О стратегии хранения данных:** Только 20 последних матчей хранятся с полной детализацией (логи покупок, таймлайны, улучшения способностей). Глобальная статистика героев (карьерные игры, победы) запрашивается из агрегированного эндпоинта OpenDota и хранится в виде плоской сводки. Это исключает неограниченный рост базы данных, сохраняя аналитическую точность.

> **О rate-ограничениях:** OpenDota применяет мягкие ограничения скорости для бесплатного доступа к API. Конвейер синхронизации вводит намеренные задержки между запросами деталей матча и реализует 2 попытки с ожиданием 3 секунды специально для эндпоинта `/heroes`, который вызывается последним в пайплайне и наиболее уязвим к исчерпанию квоты.

> **О контексте AI:** GPT-промпт получает структурированные данные матча: герой, KDA, GPM, XPM, сборка предметов с таймингами покупок (где доступно), роль на лайне, чистая стоимость, таймлайн золотого преимущества и пожизненная статистика героев игрока. Это позволяет модели контекстуализировать производительность в отдельном матче относительно исторических базовых показателей.

---

## Лицензия

Лицензия MIT. Подробности в файле [LICENSE](./LICENSE).

---

<div align="center">

Построено с точностью. Без лишнего.

</div>
