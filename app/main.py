from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.config import get_settings
from app.agents.graph import build_graph
from app.monitoring.metrics import REQUESTS, LATENCY, metrics_response
import time, structlog

log = structlog.get_logger()
app = FastAPI(title="Agentic Support Ticket Assistant")
graph = build_graph()

class TicketIn(BaseModel):
    ticket_text: str
    customer_id: str = "C-1"
    ticket_id: str | None = None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/tickets/process")
def process(t: TicketIn):
    start = time.time()
    REQUESTS.inc()
    try:
        state = {"ticket_text": t.ticket_text, "messages": [], "classification": "", "kb_context": "", "draft_response": "", "approved": False}
        out = graph.invoke(state)
        LATENCY.observe(time.time()-start)
        return {"classification": out["classification"], "draft_response": out["draft_response"], "approved": False}
    except Exception as e:
        log.error("process_failed", error=str(e))
        raise HTTPException(500, str(e))

@app.get("/metrics")
def metrics():
    return metrics_response()
def approve(payload: dict):
    # human approval gate; in real impl would trigger send
    return {"status": "approved", "ticket": payload.get("ticket_id")}
