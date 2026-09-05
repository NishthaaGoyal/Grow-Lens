# 🔭 Groww Lens — Your Market Memory

> **Transform a passive watchlist into a personalized market intelligence feed.**

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FNishthaaGoyal%2FGrow-Lens&root-directory=frontend)

Groww Lens remembers what you last saw in the market, identifies meaningful changes while you were away, ranks them by impact, and explains why they matter — powered by AI.

---

## 🧠 Core Concept

Traditional watchlists show current prices.

**Groww Lens shows:**
- What changed since your last visit
- Why it changed
- Which changes deserve attention
- What can safely be ignored

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🧠 **Market Memory Engine** | Stores snapshots of your watchlist at every session boundary |
| 🔍 **Change Detection Engine** | Compares current market data with your last snapshot |
| 📊 **Impact Scoring Engine** | Scores every event 0–100 by price, volume, news, and volatility |
| 🤖 **AI Explainability** | Gemini-powered plain-English explanations for every event |
| 📰 **Daily Market Pulse** | AI-generated mood, top sectors, and global sentiment |
| 🎯 **Attention Feed** | Card-based UI sorted by impact — no more scanning tables |

---

## 🏗 Architecture

```
groww-lens/
├── frontend/        # Next.js 15 + TypeScript + TailwindCSS + Shadcn UI
├── backend/         # FastAPI + Python + PostgreSQL + Redis
├── docs/            # Architecture diagrams and API specs
└── assets/          # Shared assets and resources
```

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Backend Setup

```bash
cd backend
cp .env.example .env
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

---

## 🔑 Environment Variables

### Backend (backend/.env)

```
DATABASE_URL=postgresql://user:password@localhost:5432/groww_lens
REDIS_URL=redis://localhost:6379
GEMINI_API_KEY=your_gemini_api_key
NEWS_API_KEY=your_newsapi_key
FINNHUB_API_KEY=your_finnhub_api_key
SECRET_KEY=your_secret_key_here
ENVIRONMENT=development
```

### Frontend (frontend/.env.local)

```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Groww Lens
```

---

## 📡 API Overview

| Endpoint | Method | Description |
|---|---|---|
| /watchlists | POST/GET | Create and list watchlists |
| /watchlists/{id}/stocks | POST/GET/DELETE | Manage stocks in a watchlist |
| /snapshots/create | POST | Capture market snapshot |
| /snapshots/latest | GET | Get last snapshot |
| /events | GET | List all events |
| /events/high-impact | GET | Events with score >= 60 |
| /dashboard/while-away | GET | The core "While You Were Away" feed |
| /dashboard/pulse | GET | Daily Market Pulse |

---

## 🗄 Database Schema

See docs/schema.sql for the full PostgreSQL schema.

---

## 📦 Tech Stack

**Frontend:** Next.js 15, TypeScript, TailwindCSS, Shadcn UI, Framer Motion, Recharts, TanStack Query

**Backend:** FastAPI, Python 3.11, SQLAlchemy, Alembic, PostgreSQL, Redis, yfinance, Gemini API

---

## 🏆 The Wow Moment

1. User creates a watchlist
2. Snapshot is stored
3. Time passes, markets move
4. User returns and sees:

> "Welcome Back. You missed 12 market events. Only 3 deserve your attention."

---

## 📄 License

MIT — Built for the Groww Lens Hackathon
