from types import SimpleNamespace

from app.tools import audit

# Test 1
## Tests that successful tool calls are persisted with the expected data.
def test_log_tool_call_persists_success(monkeypatch):
    saved = {}

    class FakeSession:
        def add(self, obj):
            saved["object"] = obj

        def commit(self):
            saved["committed"] = True

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    monkeypatch.setattr(
        audit,
        "SessionLocal",
        lambda: FakeSession(),
    )

    audit.log_tool_call(
        tool_name="get_customer",
        arguments={"customer_id": 3821},
        result={
            "id": 3821,
            "name": "Bianca",
            "status": "active",
        },
        status="success",
    )

    tool_call = saved["object"]

    assert tool_call.tool_name == "get_customer"
    assert tool_call.arguments == {"customer_id": 3821}
    assert tool_call.result == {
        "id": 3821,
        "name": "Bianca",
        "status": "active",
    }
    assert tool_call.status == "success"
    assert tool_call.ticket_id is None
    assert saved["committed"] is True

# Test 2
## Tests that failed tool calls are persisted with their error result.
def test_log_tool_call_persists_error(monkeypatch):
    saved = {}

    class FakeSession:
        def add(self, obj):
            saved["object"] = obj

        def commit(self):
            saved["committed"] = True

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    monkeypatch.setattr(
        audit,
        "SessionLocal",
        lambda: FakeSession(),
    )

    audit.log_tool_call(
        tool_name="get_customer",
        arguments={"customer_id": 3821},
        result={"error": "Database unavailable"},
        status="error",
    )

    tool_call = saved["object"]

    assert tool_call.tool_name == "get_customer"
    assert tool_call.arguments == {"customer_id": 3821}
    assert tool_call.result == {
        "error": "Database unavailable",
    }
    assert tool_call.status == "error"
    assert saved["committed"] is True

# Test 3
## Tests that an audit record can be associated with a ticket.
def test_log_tool_call_accepts_ticket_id(monkeypatch):
    saved = {}

    class FakeSession:
        def add(self, obj):
            saved["object"] = obj

        def commit(self):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    monkeypatch.setattr(
        audit,
        "SessionLocal",
        lambda: FakeSession(),
    )

    audit.log_tool_call(
        tool_name="propose_escalation",
        arguments={
            "ticket_id": 2,
            "reason": "Manual review required.",
        },
        result={"status": "pending"},
        status="success",
        ticket_id=2,
    )

    assert saved["object"].ticket_id == 2
