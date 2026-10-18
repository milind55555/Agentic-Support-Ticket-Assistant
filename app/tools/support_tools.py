import json, random
from langchain_core.tools import tool

@tool
def ticket_lookup(ticket_id: str) -> str:
    """Look up a support ticket by its ID and return status, priority, assignee."""
    # Mock backing store; replace with real ticketing API
    tickets = {
        "T-1001": {"status": "open", "priority": "high", "assignee": "alice", "summary": "VPN not connecting"},
        "T-1002": {"status": "in_progress", "priority": "medium", "assignee": "bob", "summary": "Password reset"},
    }
    t = tickets.get(ticket_id)
    if not t:
        return json.dumps({"error": "ticket not found", "ticket_id": ticket_id})
    return json.dumps({"ticket_id": ticket_id, **t})

@tool
def service_status(service: str) -> str:
    """Check current status of an IT service (vpn, email, sso, billing)."""
    statuses = {"vpn": "degraded", "email": "operational", "sso": "operational", "billing": "operational"}
    return json.dumps({"service": service, "status": statuses.get(service.lower(), "unknown")})

@tool
def customer_lookup(customer_id: str) -> str:
    """Look up customer profile by ID."""
    profiles = {"C-1": {"name": "Acme Corp", "tier": "enterprise", "sla_hours": 4}}
    p = profiles.get(customer_id, {"name": "Unknown", "tier": "standard", "sla_hours": 24})
    return json.dumps({"customer_id": customer_id, **p})

ALL_TOOLS = [ticket_lookup, service_status, customer_lookup]
