from prometheus_client import Counter, Histogram, generate_latest
from fastapi import Response

REQUESTS = Counter("tickets_processed_total", "Total tickets processed")
LATENCY = Histogram("ticket_processing_seconds", "Processing latency seconds")

def metrics_response():
    return Response(generate_latest(), media_type="text/plain")
