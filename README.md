# MoJo — Multi-Agent Orchestration System

> **MoJo Score = Output Tokens ÷ Human Input Seconds**
>
> Maximum intelligence from minimum human effort.

A FastAPI web app that orchestrates **three Claude agents in parallel** on every query, then synthesizes their outputs into one sharp brief — all in a single web request.

---

## How It Works

```
User Query
    │
    ├──▶ Research Agent     (claude-haiku)  ─┐
    ├──▶ Strategy Agent     (claude-haiku)  ─┼─▶ Synthesis Agent ─▶ MoJo Score
    └──▶ Devil's Advocate   (claude-haiku)  ─┘
```

1. **Three specialized agents fire concurrently** via `asyncio.as_completed` — no sequential waiting.
2. Each agent has a distinct system prompt tuned for its role (research, strategy, critique).
3. Results stream back to the browser via **Server-Sent Events** as each agent finishes.
4. A **synthesis agent** integrates all three perspectives into one actionable brief.
5. **MoJo Score** is displayed: `total_output_tokens / seconds_user_spent_typing`.

---

## Quick Start

```bash
pip install -r OneDrive/Desktop/MoJo/requirements.txt
export ANTHROPIC_API_KEY=sk-...
python OneDrive/Desktop/MoJo/app.py
# → http://localhost:8000
```

---

## Tech Stack

| Layer | Tool |
|---|---|
| **Backend** | Python, FastAPI, Anthropic SDK (async) |
| **Model** | `claude-haiku-4-5` — fastest Claude, ideal for parallel fan-out |
| **Parallel execution** | Python `asyncio` + `AsyncAnthropic` client |
| **Streaming** | FastAPI `StreamingResponse` + SSE → browser `ReadableStream` |
| **Frontend** | Vanilla JS + CSS (zero build tools) |
| **Deployment** | Railway (auto-deploy from GitHub) |

---

## Why High MoJo Score

- **Parallel agents** cut wall-clock latency by ~3x vs sequential calls
- **Haiku model** gives fast, cheap tokens — maximizing output/cost ratio
- **SSE streaming** means users see results as agents finish, not after all complete
- **Single web request** = zero infrastructure overhead

---

## Live Demo

Deployed on Railway — multi-agent AI orchestration accessible via web browser.

---

*Built by Venkata Rahul Murarisetty*
