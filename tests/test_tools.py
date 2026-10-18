from app.tools.support_tools import ticket_lookup, service_status, customer_lookup

def test_tools():
    assert "T-1001" in ticket_lookup.invoke({"ticket_id": "T-1001"})
    assert "operational" in service_status.invoke({"service": "email"})
    assert "Acme" in customer_lookup.invoke({"customer_id": "C-1"})
