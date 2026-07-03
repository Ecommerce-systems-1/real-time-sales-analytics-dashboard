---
title: Real-Time Sales Analytics Dashboard
emoji: 📊
colorFrom: green
colorTo: gray
sdk: docker
app_port: 7860
pinned: false
---

# Real-Time Sales Analytics Dashboard

A background generator emits a sale event every 500ms. Aggregates stream live over WebSocket /ws/stream.

The landing page is an interactive API console — click any endpoint to call the live API.

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/analytics/summary` | Aggregated snapshot |
| GET | `/api/analytics/events` | Recent raw events |
| WS | `/ws/stream` | Live aggregate stream |

## Stack

Python 3.11 · FastAPI · SQLite · Pydantic v2 · Next.js 14 (static export) · Tailwind CSS · Docker
