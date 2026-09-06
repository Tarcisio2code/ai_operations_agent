import json

from google import genai

from app.agent.tools import AGENT_TOOLS
from app.config import settings
from app.tools.customers import get_customer
from app.tools.transactions import get_transactions
from app.tools.actions import propose_escalation

client = genai.Client(api_key=settings.gemini_api_key)


TOOL_REGISTRY = {
    "get_customer": get_customer,
    "get_transactions": get_transactions,
    "propose_escalation": propose_escalation,
}

AGENT_INSTRUCTIONS = """
You are an operations support agent.

Use the available tools whenever you need factual information about
customers, transactions, or support actions.

Rules:
- Only make conclusions supported by the user's message or tool results.
- Do not invent business rules, processing times, reward-delivery behavior,
  refund behavior, account policies, or operational procedures.
- Do not assume that a completed transaction means a reward was delivered
  unless the available data explicitly says so.
- Do not assume that a pending transaction will automatically complete
  or result in a reward.
- If the available data is insufficient to determine what happened,
  say so clearly.
- You may propose an escalation when the available evidence indicates
  that human review is appropriate.
- A proposed escalation is not an approved or executed escalation.
- Never claim that an escalation was completed unless the available
  tool result explicitly confirms it.
"""

def run_agent(message: str, max_steps: int = 5) -> str:
    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=(
            f"{AGENT_INSTRUCTIONS}\n\n"
            f"User request:\n{message}"
        ),
        tools=AGENT_TOOLS,
    )

    for _ in range(max_steps):
        function_calls = [
            step
            for step in interaction.steps
            if step.type == "function_call"
        ]

        if not function_calls:
            return (
                interaction.output_text
                or "The agent did not return a response."
            )

        function_results = []

        for step in function_calls:
            tool = TOOL_REGISTRY.get(step.name)

            print(
                f"[agent] tool={step.name} "
                f"arguments={step.arguments}"
            )

            if tool is None:
                function_results.append(
                    {
                        "type": "function_result",
                        "name": step.name,
                        "call_id": step.id,
                        "result": [
                            {
                                "type": "text",
                                "text": json.dumps(
                                    {
                                        "error": (
                                            f"Unknown tool: "
                                            f"{step.name}"
                                        )
                                    }
                                ),
                            }
                        ],
                    }
                )
                continue

            try:
                result = tool(**step.arguments)

            except Exception as exc:
                result = {
                    "error": str(exc),
                }

            function_results.append(
                {
                    "type": "function_result",
                    "name": step.name,
                    "call_id": step.id,
                    "result": [
                        {
                            "type": "text",
                            "text": json.dumps(result),
                        }
                    ],
                }
            )

        if not function_results:
            return (
                interaction.output_text
                or "The agent could not execute any tool calls."
            )

        interaction = client.interactions.create(
            model="gemini-3.6-flash",
            previous_interaction_id=interaction.id,
            tools=AGENT_TOOLS,
            input=function_results,
        )

    return (
        "Agent stopped after reaching the maximum number of steps."
    )