# MoJo — Multi-Agent Orchestration System

> **MoJo Score = Output Tokens ÷ Human Input Seconds**
>
> An experimental output-volume metric; it does not measure answer quality or accuracy.

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
git clone https://github.com/venkatarahul27/MoJo.git
cd MoJo
python -m pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-...
python app.py
# → http://localhost:8000
```

---

## Tech Stack

| Layer | Tool |
|---|---|
| **Backend** | Python, FastAPI, Anthropic SDK (async) |
| **Model** | `claude-haiku-4-5-20251001` (configured in `app.py`) |
| **Parallel execution** | Python `asyncio` + `AsyncAnthropic` client |
| **Streaming** | FastAPI `StreamingResponse` + SSE → browser `ReadableStream` |
| **Frontend** | Vanilla JS + CSS (zero build tools) |
| **Deployment** | Railway configuration included |

---

## Design Notes

- The three role-based prompts run concurrently; synthesis runs after their results arrive.
- Server-Sent Events deliver completed agent results, followed by the synthesis.
- The research role uses the model's knowledge; this app does not retrieve web sources.
- Latency and API cost depend on the model and query. No comparative performance benchmark is published here.
- MoJo Score is output tokens divided by typing time, with a one-second minimum denominator. A higher score does not establish better reasoning.

## Deployment

The repository includes `Procfile` and `railway.toml` for deployment configuration. Set `ANTHROPIC_API_KEY` in the deployment environment. This README does not currently provide a public demo URL.

## Development Status

This is a portfolio prototype. Automated tests, repeatable evaluations, and production deployment hardening are future work.

## Contributing

Focused improvements to error handling, testing, and evaluation are welcome. Include reproduction steps and relevant validation with changes.

## License

[MIT](LICENSE)

---

*Built by Venkata Rahul Murarisetty*
