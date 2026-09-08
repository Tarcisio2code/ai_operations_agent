from fastapi.testclient import TestClient

from app import main

from types import SimpleNamespace

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

# Test 8
## Verifies that a ticket can be retrieved through the API.
def test_get_ticket_endpoint(monkeypatch):
    fake_ticket = SimpleNamespace(
        id=1,
        message="Customer did not receive the reward.",
        status="classified",
        category="missing_reward",
        priority="high",
        customer_id=3821,
        summary="Reward was not received.",
        escalation_reason=None,
    )

    monkeypatch.setattr(
        main,
        "get_ticket",
        lambda ticket_id: fake_ticket,
    )

    response = client.get("/tickets/1")

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "message": "Customer did not receive the reward.",
        "status": "classified",
        "category": "missing_reward",
        "priority": "high",
        "customer_id": 3821,
        "summary": "Reward was not received.",
        "escalation_reason": None,
    }

# Test 9
## Verifies that requesting a missing ticket returns HTTP 404.
def test_get_missing_ticket_returns_404(monkeypatch):
    monkeypatch.setattr(
        main,
        "get_ticket",
        lambda ticket_id: None,
    )

    response = client.get("/tickets/999999")

    assert response.status_code == 404

# Test 10
## Verifies that proposed actions for a ticket are exposed through the API.
def test_get_ticket_actions_endpoint(monkeypatch):
    monkeypatch.setattr(
        main,
        "get_ticket",
        lambda ticket_id: SimpleNamespace(id=ticket_id),
    )

    monkeypatch.setattr(
        main,
        "get_ticket_actions",
        lambda ticket_id: [
            SimpleNamespace(
                id=10,
                ticket_id=ticket_id,
                action_type="escalate_case",
                reason="Manual review required.",
                status="pending",
            )
        ],
    )

    response = client.get("/tickets/2/actions")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 10,
            "ticket_id": 2,
            "action_type": "escalate_case",
            "reason": "Manual review required.",
            "status": "pending",
        }
    ]

# Test 11
## Verifies that tool calls associated with a ticket are exposed through the API.
def test_get_ticket_tool_calls_endpoint(monkeypatch):
    monkeypatch.setattr(
        main,
        "get_ticket",
        lambda ticket_id: SimpleNamespace(id=ticket_id),
    )

    monkeypatch.setattr(
        main,
        "get_ticket_tool_calls",
        lambda ticket_id: [
            SimpleNamespace(
                id=20,
                agent_run_id=30,
                ticket_id=ticket_id,
                tool_name="propose_escalation",
                arguments={
                    "ticket_id": ticket_id,
                    "reason": "Manual review required.",
                },
                result={
                    "status": "pending",
                },
                status="success",
            )
        ],
    )

    response = client.get(
        "/tickets/2/tool-calls"
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 20,
            "agent_run_id": 30,
            "ticket_id": 2,
            "tool_name": "propose_escalation",
            "arguments": {
                "ticket_id": 2,
                "reason": "Manual review required.",
            },
            "result": {
                "status": "pending",
            },
            "status": "success",
        }
    ]

# Test 12
## Verifies that agent execution history can be retrieved through the API.
def test_get_agent_runs_endpoint(monkeypatch):
    monkeypatch.setattr(
        main,
        "get_agent_runs",
        lambda: [
            SimpleNamespace(
                id=30,
                ticket_id=2,
                user_message="Investigate ticket 2.",
                final_response=(
                    "Escalation proposed and awaiting approval."
                ),
                status="completed",
            )
        ],
    )

    response = client.get("/agent-runs")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 30,
            "ticket_id": 2,
            "user_message": "Investigate ticket 2.",
            "final_response": (
                "Escalation proposed and awaiting approval."
            ),
            "status": "completed",
        }
    ]

# Test 13
## Verifies that a single agent run can be retrieved through the API.
def test_get_agent_run_endpoint(monkeypatch):
    monkeypatch.setattr(
        main,
        "get_agent_run",
        lambda run_id: SimpleNamespace(
            id=run_id,
            ticket_id=2,
            user_message="Investigate ticket 2.",
            final_response=(
                "Escalation proposed and awaiting approval."
            ),
            status="completed",
        ),
    )

    response = client.get("/agent-runs/30")

    assert response.status_code == 200
    assert response.json() == {
        "id": 30,
        "ticket_id": 2,
        "user_message": "Investigate ticket 2.",
        "final_response": (
            "Escalation proposed and awaiting approval."
        ),
        "status": "completed",
    }

# Test 14
## Verifies that requesting a missing agent run returns HTTP 404.
def test_get_missing_agent_run_returns_404(monkeypatch):
    monkeypatch.setattr(
        main,
        "get_agent_run",
        lambda run_id: None,
    )

    response = client.get(
        "/agent-runs/999999"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Agent run not found."
    }

# Test 15
## Verifies that all tool calls for an agent run can be retrieved.
def test_get_agent_run_tool_calls_endpoint(
    monkeypatch,
):
    monkeypatch.setattr(
        main,
        "get_agent_run",
        lambda run_id: SimpleNamespace(
            id=run_id,
        ),
    )

    monkeypatch.setattr(
        main,
        "get_agent_run_tool_calls",
        lambda run_id: [
            SimpleNamespace(
                id=20,
                agent_run_id=run_id,
                ticket_id=None,
                tool_name="get_customer",
                arguments={
                    "customer_id": 3821,
                },
                result={
                    "id": 3821,
                    "name": "Bianca",
                    "status": "active",
                },
                status="success",
            ),
            SimpleNamespace(
                id=21,
                agent_run_id=run_id,
                ticket_id=None,
                tool_name="get_transactions",
                arguments={
                    "customer_id": 3821,
                },
                result=[
                    {
                        "id": 1001,
                        "customer_id": 3821,
                        "status": "completed",
                    }
                ],
                status="success",
            ),
        ],
    )

    response = client.get(
        "/agent-runs/30/tool-calls"
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 20,
            "agent_run_id": 30,
            "ticket_id": None,
            "tool_name": "get_customer",
            "arguments": {
                "customer_id": 3821,
            },
            "result": {
                "id": 3821,
                "name": "Bianca",
                "status": "active",
            },
            "status": "success",
        },
        {
            "id": 21,
            "agent_run_id": 30,
            "ticket_id": None,
            "tool_name": "get_transactions",
            "arguments": {
                "customer_id": 3821,
            },
            "result": [
                {
                    "id": 1001,
                    "customer_id": 3821,
                    "status": "completed",
                }
            ],
            "status": "success",
        },
    ]

# Test 16
## Verifies that tool calls cannot be requested for a missing agent run.
def test_get_missing_agent_run_tool_calls_returns_404(
    monkeypatch,
):
    monkeypatch.setattr(
        main,
        "get_agent_run",
        lambda run_id: None,
    )

    response = client.get(
        "/agent-runs/999999/tool-calls"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Agent run not found."
    }

# Test 17
## Verifies that a ticket is persisted before AI classification.
def test_create_ticket_persists_before_classification(
    monkeypatch,
):
    call_order = []

    created_ticket = SimpleNamespace(
        id=50,
        message="Customer 3821 did not receive a reward.",
        status="new",
    )

    classified_ticket = SimpleNamespace(
        id=50,
        message="Customer 3821 did not receive a reward.",
        status="classified",
        category="missing_reward",
        priority="high",
        customer_id=3821,
        summary="Customer did not receive a reward.",
    )

    classification = SimpleNamespace(
        category="missing_reward",
        priority="high",
        customer_id=3821,
        summary="Customer did not receive a reward.",
    )

    def create_record(message):
        call_order.append("persist")
        return created_ticket

    def classify(message):
        call_order.append("classify")
        return classification

    def save_classification(
        ticket_id,
        result,
    ):
        call_order.append("save_classification")
        return classified_ticket

    monkeypatch.setattr(
        main,
        "create_ticket_record",
        create_record,
    )

    monkeypatch.setattr(
        main,
        "classify_ticket",
        classify,
    )

    monkeypatch.setattr(
        main,
        "classify_ticket_record",
        save_classification,
    )

    response = client.post(
        "/tickets",
        json={
            "message": (
                "Customer 3821 did not receive a reward."
            )
        },
    )

    assert response.status_code == 201
    assert response.json()["id"] == 50
    assert response.json()["status"] == "classified"

    assert call_order == [
        "persist",
        "classify",
        "save_classification",
    ]


# Test 18
## Verifies that a ticket is retained when AI classification fails.
def test_create_ticket_retained_when_classification_fails(
    monkeypatch,
):
    created_ticket = SimpleNamespace(
        id=51,
        message="Customer 3821 did not receive a reward.",
        status="new",
    )

    failed_ticket_ids = []

    monkeypatch.setattr(
        main,
        "create_ticket_record",
        lambda message: created_ticket,
    )

    def fail_classification(message):
        raise RuntimeError("AI provider unavailable")

    monkeypatch.setattr(
        main,
        "classify_ticket",
        fail_classification,
    )

    monkeypatch.setattr(
        main,
        "mark_ticket_classification_failed",
        lambda ticket_id: failed_ticket_ids.append(
            ticket_id
        ),
    )

    response = client.post(
        "/tickets",
        json={
            "message": (
                "Customer 3821 did not receive a reward."
            )
        },
    )

    assert response.status_code == 503

    assert response.json() == {
        "detail": (
            "Ticket was created, but AI "
            "classification is temporarily unavailable."
        )
    }

    assert failed_ticket_ids == [51]

# Test 19
## Verifies that a ticket remains persisted when saving the successful AI classification fails.
def test_create_ticket_returns_500_when_classification_save_fails(
    monkeypatch,
):
    created_ticket = SimpleNamespace(
        id=52,
        message="Customer 3821 did not receive a reward.",
        status="new",
    )

    classification = SimpleNamespace(
        category="missing_reward",
        priority="high",
        customer_id=3821,
        summary="Customer did not receive a reward.",
    )

    monkeypatch.setattr(
        main,
        "create_ticket_record",
        lambda message: created_ticket,
    )

    monkeypatch.setattr(
        main,
        "classify_ticket",
        lambda message: classification,
    )

    def fail_classification_save(
        ticket_id,
        result,
    ):
        raise RuntimeError(
            "Database update failed"
        )

    monkeypatch.setattr(
        main,
        "classify_ticket_record",
        fail_classification_save,
    )

    response = client.post(
        "/tickets",
        json={
            "message": (
                "Customer 3821 did not receive a reward."
            )
        },
    )

    assert response.status_code == 500

    assert response.json() == {
        "detail": (
            "Ticket was created, but its "
            "classification could not be saved."
        )
    }
