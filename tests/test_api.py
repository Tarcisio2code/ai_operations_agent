from fastapi.testclient import TestClient

from app import main


client = TestClient(main.app)

# Test 1
## Verifies that the agent endpoint returns the agent response successfully.
def test_agent_endpoint_returns_response(monkeypatch):
    monkeypatch.setattr(
        main,
        "run_agent",
        lambda message: "Customer investigation completed.",
    )

    response = client.post(
        "/agent",
        json={
            "message": "Investigate customer 3821.",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "response": "Customer investigation completed."
    }

# Test 2
# Verifies that AI provider failures are exposed as a safe HTTP 503 response.
def test_agent_endpoint_returns_503_when_agent_fails(
    monkeypatch,
):
    def failing_run_agent(message):
        raise RuntimeError(
            "Gemini unavailable"
        )

    monkeypatch.setattr(
        main,
        "run_agent",
        failing_run_agent,
    )

    response = client.post(
        "/agent",
        json={
            "message": "Investigate customer 3821.",
        },
    )

    assert response.status_code == 503
    assert response.json() == {
        "detail": (
            "The AI agent is temporarily unavailable. "
            "Please try again later."
        )
    }

    # Internal provider details must not leak through the API.
    assert "Gemini unavailable" not in response.text

# Test 3
# Verifies that proposing an action for a missing ticket returns HTTP 404.
def test_create_action_returns_404_when_ticket_does_not_exist(
    monkeypatch,
):
    monkeypatch.setattr(
        main,
        "propose_escalation",
        lambda ticket_id, reason: None,
    )

    response = client.post(
        "/actions",
        json={
            "ticket_id": 999999,
            "reason": "Manual review required.",
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Ticket not found."
    }

# Test 4
## Verifies that a pending action can be approved through the API.
def test_approve_action_endpoint(monkeypatch):
    monkeypatch.setattr(
        main,
        "approve_action",
        lambda action_id: {
            "id": action_id,
            "ticket_id": 2,
            "action_type": "escalate_case",
            "reason": "Manual review required.",
            "status": "approved",
        },
    )

    response = client.post(
        "/actions/10/approve"
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 10,
        "ticket_id": 2,
        "action_type": "escalate_case",
        "reason": "Manual review required.",
        "status": "approved",
    }

# Test 5
## Verifies that a pending action can be rejected through the API.
def test_reject_action_endpoint(monkeypatch):
    monkeypatch.setattr(
        main,
        "reject_action",
        lambda action_id: {
            "id": action_id,
            "ticket_id": 2,
            "action_type": "escalate_case",
            "reason": "Manual review required.",
            "status": "rejected",
        },
    )

    response = client.post(
        "/actions/10/reject"
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 10,
        "ticket_id": 2,
        "action_type": "escalate_case",
        "reason": "Manual review required.",
        "status": "rejected",
    }

# Test 6
## Verifies that approving a missing action returns HTTP 404.
def test_approve_missing_action_returns_404(
    monkeypatch,
):
    monkeypatch.setattr(
        main,
        "approve_action",
        lambda action_id: None,
    )

    response = client.post(
        "/actions/999999/approve"
    )

    assert response.status_code == 404


# Test 7
## Verifies that rejecting a missing action returns HTTP 404.
def test_reject_missing_action_returns_404(
    monkeypatch,
):
    monkeypatch.setattr(
        main,
        "reject_action",
        lambda action_id: None,
    )

    response = client.post(
        "/actions/999999/reject"
    )

    assert response.status_code == 404
