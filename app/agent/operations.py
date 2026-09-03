import json

from google import genai

from app.agent.tools import AGENT_TOOLS
from app.config import settings
from app.tools.customers import get_customer
from app.tools.transactions import get_transactions


client = genai.Client(api_key=settings.gemini_api_key)


TOOL_REGISTRY = {
    "get_customer": get_customer,
    "get_transactions": get_transactions,
}


def run_agent(message: str) -> str:
    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=message,
        tools=AGENT_TOOLS,
    )

    for step in interaction.steps:
        if step.type != "function_call":
            continue

        tool = TOOL_REGISTRY.get(step.name)

        if tool is None:
            continue

        result = tool(**step.arguments)

        final_interaction = client.interactions.create(
            model="gemini-3.6-flash",
            previous_interaction_id=interaction.id,
            tools=AGENT_TOOLS,
            input=[
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
            ],
        )

        return final_interaction.output_text

    return interaction.output_text
    