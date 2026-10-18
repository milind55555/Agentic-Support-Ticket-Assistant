# Agentic Support Ticket Assistant

LangGraph-based agent that classifies IT/customer support tickets, searches a RAG knowledge base, calls tools (ticket lookup, service status, customer profile), drafts a response, and requires human approval before sending.

## Run
```
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Docker
```
docker-compose up --build
```

## Endpoints
- POST /tickets/process
- POST /tickets/approve
- GET /metrics
- GET /health
