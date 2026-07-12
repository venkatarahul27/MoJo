"""
MoJo — Multi-Agent Orchestration System
========================================
Three Claude agents run in parallel on every query:
  1. Research Agent   — facts, data, context
  2. Strategy Agent   — opportunities, leverage, implications
  3. Devil's Advocate — risks, counterarguments, blind spots

A fourth synthesis pass integrates all three outputs into one sharp brief.
MoJo Score = total_output_tokens / human_input_seconds
"""

import asyncio
import json
import os
import time
from typing import AsyncGenerator

import anthropic
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

app = FastAPI(title="MoJo — Multi-Agent Orchestrator")

AGENTS = [
    {
        "id": "researcher",
        "name": "Research Agent",
        "icon": "🔬",
        "color": "#4A9EFF",
        "system": (
            "You are a precision research agent. For the given topic extract and present: "
            "key facts, statistics, relevant precedents, and critical context. "
            "Be factual, specific, and cite your reasoning. Use concise bullet points."
        ),
    },
    {
        "id": "strategist",
        "name": "Strategy Agent",
        "icon": "⚡",
        "color": "#00D4AA",
        "system": (
            "You are a strategic intelligence agent. For the given topic identify: "
            "opportunities, leverage points, strategic implications, and high-impact actions. "
            "Think in systems and second-order effects. Use concise bullet points."
        ),
    },
    {
        "id": "critic",
        "name": "Devil's Advocate",
        "icon": "🎯",
        "color": "#FF6B6B",
        "system": (
            "You are a rigorous critical analysis agent. For the given topic identify: "
            "risks, failure modes, hidden assumptions, counterarguments, and blind spots. "
            "Be ruthlessly honest and specific. Use concise bullet points."
        ),
    },
]


class QueryRequest(BaseModel):
    query: str
    input_time: float  # seconds the user spent composing the query


async def run_agent(
    agent: dict, query: str, client: anthropic.AsyncAnthropic
) -> dict:
    start = time.perf_counter()
    try:
        message = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=450,
            system=agent["system"],
            messages=[{"role": "user", "content": query}],
        )
        elapsed = time.perf_counter() - start
        return {
            "id": agent["id"],
            "name": agent["name"],
            "icon": agent["icon"],
            "color": agent["color"],
            "output": message.content[0].text,
            "tokens": message.usage.output_tokens,
            "latency": round(elapsed, 2),
            "error": None,
        }
    except Exception as e:
        elapsed = time.perf_counter() - start
        return {
            "id": agent["id"],
            "name": agent["name"],
            "icon": agent["icon"],
            "color": agent["color"],
            "output": "",
            "tokens": 0,
            "latency": round(elapsed, 2),
            "error": str(e),
        }


async def run_synthesis(
    query: str, results: list, client: anthropic.AsyncAnthropic
) -> tuple[str, int]:
    context = "\n\n".join(
        [
            f"**{r['name']}**:\n{r['output']}"
            for r in results
            if not r["error"] and r["output"]
        ]
    )
    message = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=550,
        system=(
            "You are the synthesis layer of a multi-agent AI system. "
            "Given analysis from three specialized agents (Research, Strategy, Devil's Advocate), "
            "produce a sharp, integrated synthesis: key takeaways, recommended actions, "
            "and critical watch-outs. Be direct, specific, and actionable."
        ),
        messages=[
            {
                "role": "user",
                "content": f"Topic: {query}\n\n---\n\n{context}",
            }
        ],
    )
    return message.content[0].text, message.usage.output_tokens


async def event_stream(query: str, input_time: float) -> AsyncGenerator[str, None]:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        yield f"data: {json.dumps({'type': 'error', 'message': 'ANTHROPIC_API_KEY environment variable not set.'})}\n\n"
        return

    client = anthropic.AsyncAnthropic(api_key=api_key)
    total_tokens = 0
    results = []

    # Fire all 3 agents concurrently
    tasks = [
        asyncio.create_task(run_agent(agent, query, client)) for agent in AGENTS
    ]

    # Yield each result as it arrives (fastest first)
    for coro in asyncio.as_completed(tasks):
        result = await coro
        results.append(result)
        total_tokens += result["tokens"]
        yield f"data: {json.dumps({'type': 'agent', 'data': result})}\n\n"

    # Synthesis pass
    yield f"data: {json.dumps({'type': 'status', 'message': 'Synthesizing all perspectives…'})}\n\n"
    synthesis_text, synth_tokens = await run_synthesis(query, results, client)
    total_tokens += synth_tokens

    yield f"data: {json.dumps({'type': 'synthesis', 'output': synthesis_text, 'tokens': synth_tokens})}\n\n"

    # MoJo Score = output tokens / human seconds invested
    human_secs = max(input_time, 1.0)
    mojo_score = round(total_tokens / human_secs, 1)

    mojo_payload = json.dumps({
        "type": "mojo",
        "score": mojo_score,
        "total_tokens": total_tokens,
        "human_time": round(human_secs, 1),
    })
    yield f"data: {mojo_payload}\n\n"
    yield 'data: {"type":"done"}\n\n'


@app.post("/analyze")
async def analyze(request: QueryRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    return StreamingResponse(
        event_stream(request.query, request.input_time),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/", response_class=HTMLResponse)
async def root():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "index.html")
    with open(html_path, encoding="utf-8") as f:
        return HTMLResponse(f.read())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
