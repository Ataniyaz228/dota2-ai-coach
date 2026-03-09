<div align="center">

<table><tr><td align="center" bgcolor="#0d1117" style="padding:24px;border-radius:12px;">
<img src="./docs/logo.png" alt="Aegis.AI" width="360" />
</td></tr></table>

<br/>

![Build](https://img.shields.io/badge/build-passing-00c853?style=for-the-badge&labelColor=0d1117&logo=github-actions&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-15-white?style=for-the-badge&logo=next.js&labelColor=0d1117)
![Django](https://img.shields.io/badge/Django-5-092e20?style=for-the-badge&logo=django&labelColor=0d1117&color=092e20)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169e1?style=for-the-badge&logo=postgresql&labelColor=0d1117&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-Celery-dc382d?style=for-the-badge&logo=redis&labelColor=0d1117&logoColor=white)
![Gemini](https://img.shields.io/badge/Google-Gemini-4285f4?style=for-the-badge&logo=google&labelColor=0d1117&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-00e5ff?style=for-the-badge&labelColor=0d1117)

<br/>

**Aegis.AI** is a full-stack intelligence platform for Dota 2 players.  
It transforms raw match telemetry into structured, Gemini-powered coaching — ranked, visual, and brutal in precision.

<br/>

[![View Demo](https://img.shields.io/badge/-View_Demo-0d1117?style=for-the-badge&logo=youtube&logoColor=00e5ff&labelColor=0d1117)](https://github.com/Ataniyaz228/dota2-ai-coach)
[![Report Bug](https://img.shields.io/badge/-Report_Bug-0d1117?style=for-the-badge&logo=github&logoColor=ff5252&labelColor=0d1117)](https://github.com/Ataniyaz228/dota2-ai-coach/issues)
[![Star Repo](https://img.shields.io/github/stars/Ataniyaz228/dota2-ai-coach?style=for-the-badge&logo=github&labelColor=0d1117&color=ffd700)](https://github.com/Ataniyaz228/dota2-ai-coach)

</div>

---

## Demo & Screenshots

<div align="center">

<!-- PLACEHOLDER: Replace src with actual demo GIF -->
<!-- <img src="./docs/demo.gif" alt="Aegis.AI Platform Demo" width="100%" /> -->

> **[Demo GIF / Video]** — Dashboard overview, trend drill-down, AI Coach match analysis.

<br/>

<table>
  <tr>
    <td align="center">
      <img src="./docs/screenshots/landing_page.jpg" alt="Aegis.AI Landing Page" />
      <br/><sub><b>Account Input Terminal</b></sub>
    </td>
    <td align="center">
      <img src="./docs/screenshots/dashboard.jpg" alt="Aegis.AI Dashboard" />
      <br/><sub><b>Performance Dashboard</b></sub>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="./docs/screenshots/trends.png" alt="Aegis.AI Analytics Trends" />
      <br/><sub><b>Drill-down Trend Analytics</b></sub>
    </td>
    <td align="center">
      <img src="./docs/screenshots/ai_coach.jpg" alt="Aegis.AI Coach analysis" />
      <br/><sub><b>AI Coach — Match Analysis</b></sub>
    </td>
  </tr>
</table>

</div>

---

## Core Features

<table>
  <tr>
    <td width="50%" valign="top">

### Data Intelligence

![OpenDota](https://img.shields.io/badge/OpenDota-Powered-ff6f00?style=flat-square&labelColor=0d1117)

- **Lifetime Hero Statistics** — True career win/loss from OpenDota's `/heroes` endpoint, not just stored matches
- **Hybrid Data Pipeline** — Full telemetry only for last 20 matches; global stats fetched live
- **Item Purchase Timings** — Timestamped item builds from replay data surfaced in UI and AI prompts
- **Resilient Sync** — Celery worker with 2-attempt retry + 3s backoff; rate-limit failures never overwrite existing data

  </td>
    <td width="50%" valign="top">

### AI Coaching

![Gemini](https://img.shields.io/badge/Gemini-Engine-4285f4?style=flat-square&logo=google&labelColor=0d1117&logoColor=white)

- **Per-Match Analysis** — Structured Gemini prompt with hero, KDA, GPM, items, timing, laning role, net worth
- **Conversational Context** — Follow-up questions retain full match context in unified chat interface
- **Historical Baseline** — AI contextualizes individual match vs. lifetime hero performance
- **No Fragmented UI** — Single scrollable conversation, no nested panels, no internal scrollbars

  </td>
  </tr>
  <tr>
    <td width="50%" valign="top">

### Analytics & Visualization

![Recharts](https://img.shields.io/badge/Recharts-Charts-22b5bf?style=flat-square&labelColor=0d1117)

- **Drill-down Trend Charts** — GPM, KDA, XPM, Last Hits, Hero Damage across last 30 matches
- **Clickable Data Points** — Chart nodes navigate directly to full match detail view
- **Smart Rank Mapping** — Rank tier integers decoded to Herald–Immortal with MMR range estimates
- **Lifetime W/L Block** — Wins / Losses / Winrate displayed like OpenDota's header, always accurate

  </td>
    <td width="50%" valign="top">

### Design System

![Dark Mode](https://img.shields.io/badge/Dark--Mode-Only-0d1117?style=flat-square&labelColor=111827&color=00e5ff)

- **Architectural Minimalism** — No decorative gradients, no emoji, every element earns its place
- **Custom CSS Design System** — Tokens, utilities, and components in Vanilla CSS — no Tailwind
- **Micro-interactions** — Hover states, chart animations, status pulse dots
- **Responsive Layout** — Grid system adapts from wide dashboard to compact mobile view

  </td>
  </tr>
</table>

---

## Architecture

```
 Client Browser
       |
       | HTTPS
       v
 ┌─────────────────────────────────────────┐
 │            Next.js 15                   │
 │   App Router  ·  TypeScript  ·  CSS     │
 │   Recharts  ·  ReactMarkdown            │
 └────────────────────┬────────────────────┘
                      │ REST / JSON
                      v
 ┌─────────────────────────────────────────┐
 │        Django 5  +  DRF                 │
 │                                         │
 │  /api/v1/profile/   /api/v1/dashboard/  │
 │  /api/v1/coach/     /api/v1/heroes/     │
 └──────┬─────────────────────┬────────────┘
        │                     │
        v                     v
 ┌──────────────┐    ┌────────────────────┐
 │  PostgreSQL  │    │  Celery  +  Redis  │
 │              │    │                    │
 │  Player      │    │  sync_player_data  │
 │  Match       │    │  _sync_profile     │
 │  PlayerMatch │    │  _sync_matches     │
 │  HeroStats   │    │  _update_hero_stats│
 └──────────────┘    └────────┬───────────┘
                              │
               ┌──────────────┴──────────────┐
               │                             │
               v                             v
 ┌─────────────────────┐        ┌────────────────────────┐
 │   OpenDota API      │        │    Google Gemini       │
 │                     │        │                        │
 │  /players/{id}      │        │  Match analysis prompt │
 │  /players/{id}/wl   │        │  Conversational chat   │
 │  Structured context │        │  Item timing & history │
 │  /matches/{id}      │        └────────────────────────┘
 └─────────────────────┘
```

### Tech Stack

| Layer | Technology | Purpose |
|:---|:---|:---|
| ![Next.js](https://img.shields.io/badge/-Next.js-black?logo=next.js&style=flat-square) | Next.js 15 (App Router) | Frontend framework, SSR, routing |
| ![TS](https://img.shields.io/badge/-TypeScript-3178c6?logo=typescript&logoColor=white&style=flat-square) | TypeScript | Type safety across all frontend code |
| ![CSS](https://img.shields.io/badge/-Vanilla_CSS-1572B6?logo=css3&logoColor=white&style=flat-square) | Vanilla CSS | Custom design system, no Tailwind |
| ![Recharts](https://img.shields.io/badge/-Recharts-22b5bf?style=flat-square) | Recharts | Interactive performance charts |
| ![Django](https://img.shields.io/badge/-Django-092e20?logo=django&logoColor=white&style=flat-square) | Django 5 + DRF | REST API, ORM, serializers |
| ![Celery](https://img.shields.io/badge/-Celery-37814a?logo=celery&logoColor=white&style=flat-square) | Celery + Redis | Async sync pipeline, background tasks |
| ![PG](https://img.shields.io/badge/-PostgreSQL-4169e1?logo=postgresql&logoColor=white&style=flat-square) | PostgreSQL | Primary datastore |
| ![OD](https://img.shields.io/badge/-OpenDota_API-ff6f00?style=flat-square) | OpenDota API | Free Dota 2 stats, no key needed |
| ![Gemini](https://img.shields.io/badge/-Gemini-4285f4?logo=google&logoColor=white&style=flat-square) | Google Gemini | Match analysis and coaching engine |

---

## Getting Started

### Prerequisites

![Python](https://img.shields.io/badge/Python-3.12+-3776ab?style=flat-square&logo=python&logoColor=white)
![Node](https://img.shields.io/badge/Node.js-20+-339933?style=flat-square&logo=node.js&logoColor=white)
![PG](https://img.shields.io/badge/PostgreSQL-required-4169e1?style=flat-square&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-required-dc382d?style=flat-square&logo=redis&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-API_Key-4285f4?style=flat-square&logo=google&logoColor=white)

### 1. Clone

```bash
git clone https://github.com/Ataniyaz228/dota2-ai-coach.git
cd dota2-ai-coach
```

### 2. Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux / macOS
# source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:

```env
DATABASE_URL=postgres://user:password@localhost:5432/aegis
REDIS_URL=redis://localhost:6379/0
LLM_API_KEY=your-gemini-compatible-key
LLM_BASE_URL=http://127.0.0.1:8045/v1
LLM_MODEL=gemini-2.5-pro
SECRET_KEY=your-django-secret-key
DEBUG=True
```

```bash
python manage.py migrate
python manage.py runserver
```

Start background worker (separate terminal):

```bash
celery -A config worker -l info --pool=solo
```

### 3. Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
```

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

```bash
npm run dev
```

> Platform available at `http://localhost:3000`  
> Enter any **public** Dota 2 Account ID on the landing page to trigger synchronization.

---

## Data Flow

```
 User enters Account ID
          |
          v
 POST /api/v1/profile/link
          |
          v
 Celery: sync_player_data(account_id)
    |
    |─── _sync_profile()
    |         OpenDota: /players/{id}
    |         OpenDota: /players/{id}/wl  (lifetime W/L)
    |
    |─── _sync_matches()
    |         OpenDota: /players/{id}/matches  (list)
    |         OpenDota: /matches/{id}           (detail × last 20)
    |             -> kills, items, purchase_log, timelines
    |
    |─── _update_hero_stats()
              OpenDota: /players/{id}/heroes   [retry × 2, 3s backoff]
              Merge: global games/wins + local avg KDA/GPM/XPM
              Write: PlayerHeroStats (upsert)
                         |
                         v
              PostgreSQL committed
                         |
                         v
              Dashboard API: merged lifetime + recent data
```

---

## Architectural Notes

> **Hybrid Storage:** Full match telemetry (purchase logs, timelines, ability upgrades) is stored for the 20 most recent matches only. Global hero stats (career games, wins) are fetched from OpenDota's aggregated endpoint as a flat summary. This prevents unbounded DB growth while preserving analytical accuracy.

> **Rate Limit Resilience:** The `/heroes` endpoint is called last in the sync pipeline, after 20+ match detail requests. A 2-attempt retry with 3-second backoff is applied. If both fail, the function exits cleanly — existing hero stats are **never overwritten** with degraded data.

> **AI Prompt Scope:** The GPT context includes: hero, KDA, GPM, XPM, item build with purchase timings, laning role, net worth, gold advantage timeline, and lifetime hero stats. This allows the model to contextualize each match against the player's historical baseline.

---

<div align="center">

![Made with precision](https://img.shields.io/badge/Made_with-Precision-00e5ff?style=for-the-badge&labelColor=0d1117)
![No fluff](https://img.shields.io/badge/No-Fluff-0d1117?style=for-the-badge&labelColor=0d1117&color=ff5252)

</div>

---
---

<!-- ============================================================ -->
<!-- RUSSIAN VERSION / РУССКАЯ ВЕРСИЯ -->
<!-- ============================================================ -->

<div align="center">

<table><tr><td align="center" bgcolor="#0d1117" style="padding:24px;border-radius:12px;">
<img src="./docs/logo.png" alt="Aegis.AI" width="360" />
</td></tr></table>

<br/>

![Сборка](https://img.shields.io/badge/сборка-успешна-00c853?style=for-the-badge&labelColor=0d1117&logo=github-actions&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-15-white?style=for-the-badge&logo=next.js&labelColor=0d1117)
![Django](https://img.shields.io/badge/Django-5-092e20?style=for-the-badge&logo=django&labelColor=0d1117&color=092e20)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169e1?style=for-the-badge&logo=postgresql&labelColor=0d1117&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-Celery-dc382d?style=for-the-badge&logo=redis&labelColor=0d1117&logoColor=white)
![Gemini](https://img.shields.io/badge/Google-Gemini-4285f4?style=for-the-badge&logo=google&labelColor=0d1117&logoColor=white)
![Лицензия](https://img.shields.io/badge/Лицензия-MIT-00e5ff?style=for-the-badge&labelColor=0d1117)

<br/>

**Aegis.AI** — полностековая платформа интеллектуального анализа для игроков в Dota 2.  
Превращает сырые данные матчей в структурированный, Gemini-анализ с ранговыми метриками, визуализацией и хирургической точностью.

<br/>

[![Смотреть демо](https://img.shields.io/badge/-Смотреть_демо-0d1117?style=for-the-badge&logo=youtube&logoColor=00e5ff&labelColor=0d1117)](https://github.com/Ataniyaz228/dota2-ai-coach)
[![Сообщить о баге](https://img.shields.io/badge/-Сообщить_об_ошибке-0d1117?style=for-the-badge&logo=github&logoColor=ff5252&labelColor=0d1117)](https://github.com/Ataniyaz228/dota2-ai-coach/issues)
[![Звезда](https://img.shields.io/github/stars/Ataniyaz228/dota2-ai-coach?style=for-the-badge&logo=github&labelColor=0d1117&color=ffd700)](https://github.com/Ataniyaz228/dota2-ai-coach)

</div>

---

## Демо и скриншоты

<div align="center">

<!-- PLACEHOLDER: Замените на реальный GIF -->
<!-- <img src="./docs/demo.gif" alt="Демо платформы Aegis.AI" width="100%" /> -->

> **[Demo GIF / Video]** — Обзор дашборда, детализация трендов, AI-анализ матча.

<br/>

<table>
  <tr>
    <td align="center">
      <img src="./docs/screenshots/landing_page.jpg" alt="Aegis.AI Landing Page — RU" />
      <br/><sub><b>Ввод аккаунта</b></sub>
    </td>
    <td align="center">
      <img src="./docs/screenshots/dashboard.jpg" alt="Aegis.AI Dashboard — RU" />
      <br/><sub><b>Общая статистика</b></sub>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="./docs/screenshots/trends.png" alt="Aegis.AI Trends — RU" />
      <br/><sub><b>Аналитика трендов</b></sub>
    </td>
    <td align="center">
      <img src="./docs/screenshots/ai_coach.jpg" alt="Aegis.AI Coach — RU" />
      <br/><sub><b>AI Coach — Анализ матча</b></sub>
    </td>
  </tr>
</table>

</div>

---

## Ключевые возможности

<table>
  <tr>
    <td width="50%" valign="top">

### Анализ данных

![OpenDota](https://img.shields.io/badge/OpenDota-Powered-ff6f00?style=flat-square&labelColor=0d1117)

- **Статистика героев за всю карьеру** — Реальные данные из `/heroes` OpenDota, не только локальные матчи
- **Гибридный пайплайн** — Полная телеметрия только для 20 последних матчей; глобальные агрегаты в реальном времени
- **Тайминги предметов** — Временные метки покупок из данных реплея в UI и AI-промптах
- **Устойчивая синхронизация** — Celery с 2 попытками и 3-секундным ожиданием; сбои не перезаписывают данные

  </td>
    <td width="50%" valign="top">

### AI-коучинг

![Gemini](https://img.shields.io/badge/Gemini-Engine-4285f4?style=flat-square&logo=google&labelColor=0d1117&logoColor=white)

- **Анализ каждого матча** — Структурированный промпт: герой, KDA, GPM, предметы, тайминги, роль, нетворс
- **Разговорный контекст** — Уточняющие вопросы сохраняют контекст матча в едином чате
- **Исторический базис** — AI сравнивает матч с карьерной статистикой героя
- **Без фрагментации UI** — Один скроллируемый чат, нет вложенных панелей или скроллбаров

  </td>
  </tr>
  <tr>
    <td width="50%" valign="top">

### Визуализация

![Recharts](https://img.shields.io/badge/Recharts-Charts-22b5bf?style=flat-square&labelColor=0d1117)

- **Drill-down графики** — GPM, KDA, XPM, Last Hits, урон по строениям за 30 матчей
- **Кликабельные точки** — Переход на детализацию матча прямо из графика
- **Умная расшифровка ранга** — От Herald 1 до Immortal с диапазоном MMR
- **Блок побед/поражений** — Как в OpenDota: Победы / Поражения / Доля побед, всегда актуально

  </td>
    <td width="50%" valign="top">

### Дизайн-система

![Dark Mode](https://img.shields.io/badge/Dark--Mode-Only-0d1117?style=flat-square&labelColor=111827&color=00e5ff)

- **Архитектурный минимализм** — Нет декоративных градиентов, нет эмодзи, каждый элемент оправдан
- **Vanilla CSS** — Собственная дизайн-система с токенами и утилитами, без Tailwind
- **Микро-анимации** — Hover-эффекты, анимации графиков, пульсирующие точки статуса
- **Адаптивный лейаут** — Grid-система от широкого дашборда до мобильного вида

  </td>
  </tr>
</table>

---

## Архитектура

```
 Браузер клиента
       |
       | HTTPS
       v
 ┌─────────────────────────────────────────┐
 │            Next.js 15                   │
 │   App Router  ·  TypeScript  ·  CSS     │
 │   Recharts  ·  ReactMarkdown            │
 └────────────────────┬────────────────────┘
                      │ REST / JSON
                      v
 ┌─────────────────────────────────────────┐
 │        Django 5  +  DRF                 │
 │                                         │
 │  /api/v1/profile/   /api/v1/dashboard/  │
 │  /api/v1/coach/     /api/v1/heroes/     │
 └──────┬─────────────────────┬────────────┘
        │                     │
        v                     v
 ┌──────────────┐    ┌────────────────────┐
 │  PostgreSQL  │    │  Celery  +  Redis  │
 │              │    │                    │
 │  Player      │    │  sync_player_data  │
 │  Match       │    │  _sync_profile     │
 │  PlayerMatch │    │  _sync_matches     │
 │  HeroStats   │    │  _update_hero_stats│
 └──────────────┘    └────────┬───────────┘
                              │
               ┌──────────────┴──────────────┐
               │                             │
               v                             v
 ┌─────────────────────┐        ┌────────────────────────┐
 │   OpenDota API      │        │    Google Gemini       │
 │                     │        │                        │
 │  /players/{id}      │        │  Структурированный     │
 │  /players/{id}/wl   │        │  промпт матча          │
 │  /players/{id}/heroes│        │  Контекст разговора   │
 │  /matches/{id}      │        └────────────────────────┘
 └─────────────────────┘
```

### Стек технологий

| Слой | Технология | Назначение |
|:---|:---|:---|
| ![Next.js](https://img.shields.io/badge/-Next.js-black?logo=next.js&style=flat-square) | Next.js 15 | Фронтенд, SSR, маршрутизация |
| ![TS](https://img.shields.io/badge/-TypeScript-3178c6?logo=typescript&logoColor=white&style=flat-square) | TypeScript | Типизация фронтенда |
| ![CSS](https://img.shields.io/badge/-Vanilla_CSS-1572B6?logo=css3&logoColor=white&style=flat-square) | Vanilla CSS | Дизайн-система без Tailwind |
| ![Recharts](https://img.shields.io/badge/-Recharts-22b5bf?style=flat-square) | Recharts | Интерактивные графики |
| ![Django](https://img.shields.io/badge/-Django-092e20?logo=django&logoColor=white&style=flat-square) | Django 5 + DRF | REST API, ORM, сериализаторы |
| ![Celery](https://img.shields.io/badge/-Celery-37814a?logo=celery&logoColor=white&style=flat-square) | Celery + Redis | Асинхронный пайплайн синхронизации |
| ![PG](https://img.shields.io/badge/-PostgreSQL-4169e1?logo=postgresql&logoColor=white&style=flat-square) | PostgreSQL | Основное хранилище |
| ![OD](https://img.shields.io/badge/-OpenDota_API-ff6f00?style=flat-square) | OpenDota API | Данные Dota 2, ключ не нужен |
| ![Gemini](https://img.shields.io/badge/-Gemini-4285f4?logo=google&logoColor=white&style=flat-square) | Google Gemini | Движок анализа и коучинга |

---

## Быстрый старт

### Требования

![Python](https://img.shields.io/badge/Python-3.12+-3776ab?style=flat-square&logo=python&logoColor=white)
![Node](https://img.shields.io/badge/Node.js-20+-339933?style=flat-square&logo=node.js&logoColor=white)
![PG](https://img.shields.io/badge/PostgreSQL-обязательно-4169e1?style=flat-square&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-обязательно-dc382d?style=flat-square&logo=redis&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-API_ключ-4285f4?style=flat-square&logo=google&logoColor=white)

### 1. Клонирование

```bash
git clone https://github.com/Ataniyaz228/dota2-ai-coach.git
cd dota2-ai-coach
```

### 2. Бэкенд

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux / macOS
# source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

Заполните `.env`:

```env
DATABASE_URL=postgres://user:password@localhost:5432/aegis
REDIS_URL=redis://localhost:6379/0
LLM_API_KEY=your-gemini-compatible-key
LLM_BASE_URL=http://127.0.0.1:8045/v1
LLM_MODEL=gemini-3.1-pro-high
SECRET_KEY=ваш-django-секретный-ключ
DEBUG=True
```

```bash
python manage.py migrate
python manage.py runserver
```

Воркер (отдельный терминал):

```bash
celery -A config worker -l info --pool=solo
```

### 3. Фронтенд

```bash
cd frontend
npm install
cp .env.local.example .env.local
```

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

```bash
npm run dev
```

> Платформа доступна по адресу `http://localhost:3000`  
> Введите любой **публичный** Account ID Dota 2 на главной странице для запуска синхронизации.

---

## Архитектурные примечания

> **Гибридное хранение:** Полная телеметрия матча (логи покупок, таймлайны, улучшения способностей) сохраняется только для 20 последних матчей. Глобальная статистика героев запрашивается из агрегированного эндпоинта OpenDota. Это исключает неограниченный рост базы данных без потери аналитической точности.

> **Устойчивость к rate-limit:** Эндпоинт `/heroes` вызывается последним в пайплайне, после 20+ запросов деталей матча. Применяется 2 попытки с ожиданием 3 секунды. При неудаче функция завершается корректно — существующие данные героев **никогда не перезаписываются** деградированными.

> **Контекст AI-промпта:** Gemini получает: герой, KDA, GPM, XPM, сборка предметов с таймингами, роль на лайне, нетворс, таймлайн золотого преимущества и пожизненная статистика героя. Это позволяет модели соотнести производительность в матче с историческим базисом игрока.

---

## Лицензия

MIT License. Подробности в файле [LICENSE](./LICENSE).

---

<div align="center">

![Made with precision](https://img.shields.io/badge/Сделано_с-точностью-00e5ff?style=for-the-badge&labelColor=0d1117)
![No fluff](https://img.shields.io/badge/Без-лишнего-0d1117?style=for-the-badge&labelColor=0d1117&color=ff5252)

</div>
