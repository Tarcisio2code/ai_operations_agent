from types import SimpleNamespace

from app.agent import operations

# Test 1
## Tests a basic agent flow with a single read-only tool call.
def test_agent_executes_get_customer(monkeypatch):
    calls = []

    first_interaction = SimpleNamespace(
        id="interaction-1",
        steps=[
            SimpleNamespace(
                type="function_call",
                name="get_customer",
                arguments={"customer_id": 3821},
                id="call-1",
            )
        ],
        output_text="",
    )

    second_interaction = SimpleNamespace(
        id="interaction-2",
        steps=[],
        output_text="Customer 3821 is active.",
    )

    responses = iter(
        [
            first_interaction,
            second_interaction,
        ]
    )

    def fake_create(**kwargs):
        calls.append(kwargs)
        return next(responses)

    monkeypatch.setattr(
        operations.client.interactions,
        "create",
        fake_create,
    )

    monkeypatch.setitem(
        operations.TOOL_REGISTRY,
        "get_customer",
        lambda customer_id: {
            "id": customer_id,
            "name": "Bianca",
            "status": "active",
        },
    )

    result = operations.run_agent(
        "Tell me about customer 3821."
    )

    assert result == "Customer 3821 is active."
    assert len(calls) == 2

    assert calls[0]["tools"] == operations.AGENT_TOOLS

    assert calls[1]["previous_interaction_id"] == "interaction-1"
    assert calls[1]["tools"] == operations.AGENT_TOOLS

# Test 2
## Tests that the agent can create a pending escalation proposal.
def test_agent_can_propose_escalation(monkeypatch):
    executed = {}

    first_interaction = SimpleNamespace(
        id="interaction-1",
        steps=[
            SimpleNamespace(
                type="function_call",
                name="propose_escalation",
                arguments={
                    "ticket_id": 2,
                    "reason": "Manual review required.",
                },
                id="call-1",
            )
        ],
        output_text="",
    )

    second_interaction = SimpleNamespace(
        id="interaction-2",
        steps=[],
        output_text="Escalation proposed and awaiting approval.",
    )

    responses = iter(
        [
            first_interaction,
            second_interaction,
        ]
    )

    def fake_create(**kwargs):
        return next(responses)

    monkeypatch.setattr(
        operations.client.interactions,
        "create",
        fake_create,
    )

    def fake_propose_escalation(ticket_id, reason):
        executed["ticket_id"] = ticket_id
        executed["reason"] = reason

        return {
            "id": 10,
            "ticket_id": ticket_id,
            "action_type": "escalate_case",
            "reason": reason,
            "status": "pending",
        }

    monkeypatch.setitem(
        operations.TOOL_REGISTRY,
        "propose_escalation",
        fake_propose_escalation,
    )

    result = operations.run_agent(
        "Investigate ticket 2."
    )

    assert executed["ticket_id"] == 2
    assert executed["reason"] == "Manual review required."

    assert result == (
        "Escalation proposed and awaiting approval."
    )

# Test 3
## Tests that the agent can execute multiple tool calls in one interaction.
def test_agent_executes_multiple_tools(monkeypatch):
    executed = []

    first_interaction = SimpleNamespace(
        id="interaction-1",
        steps=[
            SimpleNamespace(
                type="function_call",
                name="get_customer",
                arguments={"customer_id": 3821},
                id="call-customer",
            ),
            SimpleNamespace(
                type="function_call",
                name="get_transactions",
                arguments={"customer_id": 3821},
                id="call-transactions",
            ),
        ],
        output_text="",
    )

    second_interaction = SimpleNamespace(
        id="interaction-2",
        steps=[],
        output_text="Investigation completed.",
    )

    responses = iter(
        [
            first_interaction,
            second_interaction,
        ]
    )

    def fake_create(**kwargs):
        return next(responses)

    monkeypatch.setattr(
        operations.client.interactions,
        "create",
        fake_create,
    )

    def fake_get_customer(customer_id):
        executed.append(
            ("get_customer", customer_id)
        )

        return {
            "id": customer_id,
            "name": "Bianca",
            "status": "active",
        }

    def fake_get_transactions(customer_id):
        executed.append(
            ("get_transactions", customer_id)
        )

        return [
            {
                "id": 1001,
                "customer_id": customer_id,
                "offer_id": "offer-apple-01",
                "amount": 25.0,
                "status": "completed",
            }
        ]

    monkeypatch.setitem(
        operations.TOOL_REGISTRY,
        "get_customer",
        fake_get_customer,
    )

    monkeypatch.setitem(
        operations.TOOL_REGISTRY,
        "get_transactions",
        fake_get_transactions,
    )

    result = operations.run_agent(
        "Investigate customer 3821."
    )

    assert executed == [
        ("get_customer", 3821),
        ("get_transactions", 3821),
    ]

    assert result == "Investigation completed."

# Test 4
## Tests that the agent cannot approve or directly execute escalations.
def test_agent_cannot_approve_or_execute_escalation():
    assert "approve_action" not in operations.TOOL_REGISTRY
    assert "escalate_case" not in operations.TOOL_REGISTRY

    available_tool_names = {
        tool["name"]
        for tool in operations.AGENT_TOOLS
    }

    assert "approve_action" not in available_tool_names
    assert "escalate_case" not in available_tool_names

    assert "propose_escalation" in available_tool_names

# Test 5
## Tests that unknown tool calls are returned to the agent as errors.
def test_agent_handles_unknown_tool(monkeypatch):
    first_interaction = SimpleNamespace(
        id="interaction-1",
        steps=[
            SimpleNamespace(
                type="function_call",
                name="unknown_tool",
                arguments={},
                id="call-1",
            )
        ],
        output_text="",
    )

    second_interaction = SimpleNamespace(
        id="interaction-2",
        steps=[],
        output_text="The requested tool is not available.",
    )

    responses = iter(
        [
            first_interaction,
            second_interaction,
        ]
    )

    calls = []

    def fake_create(**kwargs):
        calls.append(kwargs)
        return next(responses)

    monkeypatch.setattr(
        operations.client.interactions,
        "create",
        fake_create,
    )

    result = operations.run_agent(
        "Use an unavailable tool."
    )

    assert result == "The requested tool is not available."

    tool_result = calls[1]["input"][0]

    assert tool_result["name"] == "unknown_tool"
    assert "Unknown tool" in tool_result["result"][0]["text"]

# Test 6
## Tests that tool exceptions are converted into agent-readable errors.
def test_agent_handles_tool_exception(monkeypatch):
    first_interaction = SimpleNamespace(
        id="interaction-1",
        steps=[
            SimpleNamespace(
                type="function_call",
                name="get_customer",
                arguments={"customer_id": 3821},
                id="call-1",
            )
        ],
        output_text="",
    )

    second_interaction = SimpleNamespace(
        id="interaction-2",
        steps=[],
        output_text="Customer data could not be retrieved.",
    )

    responses = iter(
        [
            first_interaction,
            second_interaction,
        ]
    )

    calls = []

    def fake_create(**kwargs):
        calls.append(kwargs)
        return next(responses)

    monkeypatch.setattr(
        operations.client.interactions,
        "create",
        fake_create,
    )

    def failing_get_customer(customer_id):
        raise RuntimeError("Database unavailable")

    monkeypatch.setitem(
        operations.TOOL_REGISTRY,
        "get_customer",
        failing_get_customer,
    )

    result = operations.run_agent(
        "Tell me about customer 3821."
    )

    assert result == "Customer data could not be retrieved."

    tool_result = calls[1]["input"][0]

    assert tool_result["name"] == "get_customer"
    assert "Database unavailable" in tool_result["result"][0]["text"]

# Test 7
## Tests that the agent stops when the maximum tool-call steps are reached.
def test_agent_stops_after_max_steps(monkeypatch):
    counter = {"value": 0}

    def fake_create(**kwargs):
        counter["value"] += 1

        return SimpleNamespace(
            id=f"interaction-{counter['value']}",
            steps=[
                SimpleNamespace(
                    type="function_call",
                    name="get_customer",
                    arguments={"customer_id": 3821},
                    id=f"call-{counter['value']}",
                )
            ],
            output_text="",
        )

    monkeypatch.setattr(
        operations.client.interactions,
        "create",
        fake_create,
    )

    monkeypatch.setitem(
        operations.TOOL_REGISTRY,
        "get_customer",
        lambda customer_id: {
            "id": customer_id,
            "status": "active",
        },
    )

    result = operations.run_agent(
        "Keep checking customer 3821.",
        max_steps=3,
    )

    assert result == (
        "Agent stopped after reaching the maximum number of steps."
    )

    assert counter["value"] == 4
    