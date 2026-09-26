# Personal Tech Radar

A personal technology intelligence platform: collects tech news from RSS
feeds, Hacker News, and GitHub, analyzes it with AI against your profile,
and delivers a concise daily briefing via Telegram — plus this web
dashboard.

> The internet produces thousands of technology updates → the system
> identifies what matters → you receive a concise personalized daily
> briefing.

The full product specification lives in [GOAL.md](./GOAL.md).

## Stack

| Layer    | Tech                                                            |
| -------- | --------------------------------------------------------------- |
| Backend  | FastAPI, SQLAlchemy 2 (async), Alembic, Postgres, Redis, uv     |
| AI       | OpenAI-compatible provider (Z.AI default), Pydantic-validated   |
| Delivery | Telegram bot + Next.js dashboard                                |
| Frontend | Next.js 16, React 19, Tailwind v4, shadcn/ui, pnpm              |

## Quickstart

```bash
make setup        # env files + install deps + postgres/redis + migrations
make dev          # backend :7101 + frontend :3200
```

Then:

1. Put your keys in `backend/.env` (`AI_API_KEY`, `TELEGRAM_BOT_TOKEN`,
   `TELEGRAM_CHAT_ID`).
2. Seed a few sources: `POST /api/sources` (see `/docs`).
3. Run the pipeline:

```bash
make collect          # fetch from all enabled sources
make analyze          # AI analysis of new items
make generate-digest  # rank + select + build today's digest
make send-digest      # deliver to Telegram
# or everything at once:
make run-daily
```

## Layout

```
backend/            FastAPI app (main.py, core/, models/, modules/)
  modules/          profile, sources, content, digests, feedback (API)
                    ingestion, ai, notifications, scheduler (pipeline)
frontend/           Next.js dashboard (src/app, src/components, src/lib)
compose.yaml        postgres + redis + backend + frontend
GOAL.md             full product spec
```

## Quality gates

```bash
make check          # pyright + ruff + frontend lint + build
```
