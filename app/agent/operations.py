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

def run_agent(message: str, max_steps: int = 5) -> str:
    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=message,
        tools=AGENT_TOOLS,
    )

    for _ in range(max_steps):
        function_calls = [
            step
            for step in interaction.steps
            if step.type == "function_call"
        ]

        if not function_calls:
            return interaction.output_text

        function_results = []

        for step in function_calls:
            tool = TOOL_REGISTRY.get(step.name)

            if tool is None:
                continue

            result = tool(**step.arguments)

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
            return interaction.output_text

        interaction = client.interactions.create(
            model="gemini-3.6-flash",
            previous_interaction_id=interaction.id,
            tools=AGENT_TOOLS,
            input=function_results,
        )

    return "Agent stopped after reaching the maximum number of steps."