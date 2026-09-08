from types import SimpleNamespace

from app.tools import actions

# Test 1
## Tests that rejecting a pending action changes only the action status.
def test_reject_action_marks_pending_action_as_rejected(monkeypatch):
    fake_action = SimpleNamespace(
        id=3,
        ticket_id=2,
        action_type="escalate_case",
        reason="Manual review requested.",
        status="pending",
    )

    class FakeSession:
        def scalar(self, query):
            return fake_action

        def commit(self):
            pass

        def refresh(self, obj):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    monkeypatch.setattr(
        actions,
        "SessionLocal",
        lambda: FakeSession(),
    )

    result = actions.reject_action(3)

    assert fake_action.status == "rejected"

    assert result == {
        "id": 3,
        "ticket_id": 2,
        "action_type": "escalate_case",
        "reason": "Manual review requested.",
        "status": "rejected",
    }

# Test 2
## Tests that rejecting a missing action returns None.
def test_reject_action_returns_none_when_action_does_not_exist(
    monkeypatch,
):
    class FakeSession:
        def scalar(self, query):
            return None

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    monkeypatch.setattr(
        actions,
        "SessionLocal",
        lambda: FakeSession(),
    )

    result = actions.reject_action(9999)

    assert result is None
