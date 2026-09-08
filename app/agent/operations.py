import json

from google import genai

from app.agent.tools import AGENT_TOOLS

from app.config import settings

from app.tools.customers import get_customer
from app.tools.transactions import get_transactions
from app.tools.actions import propose_escalation
from app.tools.audit import log_tool_call
from app.tools.runs import complete_agent_run, create_agent_run, fail_agent_run

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
    run_ticket_id = None

    agent_run_id = create_agent_run(
        user_message=message,
    )

    try:
        interaction = client.interactions.create(
            model="gemini-3.6-flash",
            input=(
                f"{AGENT_INSTRUCTIONS}\n\n"
                f"User request:\n{message}"
            ),
            tools=AGENT_TOOLS,
        )

    except Exception:
        fail_agent_run(
            run_id=agent_run_id,
            final_response="Agent execution failed.",
        )

        raise

    for _ in range(max_steps):
        function_calls = [
            step
            for step in interaction.steps
            if step.type == "function_call"
        ]

        if not function_calls:
            final_response = (
                interaction.output_text
                or "The agent did not return a response."
            )

            complete_agent_run(
                run_id=agent_run_id,
                final_response=final_response,
                status="completed",
                ticket_id=run_ticket_id,
            )

            return final_response

        function_results = []

        for step in function_calls:
            tool = TOOL_REGISTRY.get(step.name)

            ticket_id = step.arguments.get("ticket_id")
            if ticket_id is not None:
                run_ticket_id = ticket_id

            print(
                f"[agent] tool={step.name} "
                f"arguments={step.arguments}"
            )

            if tool is None:
                error_result = {
                    "error": f"Unknown tool: {step.name}"
                }

                log_tool_call(
                    tool_name=step.name,
                    arguments=step.arguments,
                    result=error_result,
                    status="error",
                    ticket_id=ticket_id,
                    agent_run_id=agent_run_id,
                )

                function_results.append(
                    {
                        "type": "function_result",
                        "name": step.name,
                        "call_id": step.id,
                        "result": [
                            {
                                "type": "text",
                                "text": json.dumps(error_result),
                            }
                        ],
                    }
                )
                continue

            try:
                result = tool(**step.arguments)

                log_tool_call(
                    tool_name=step.name,
                    arguments=step.arguments,
                    result=result,
                    status="success",
                    ticket_id=ticket_id,
                    agent_run_id=agent_run_id,
                )

            except Exception as exc:
                result = {
                    "error": str(exc),
                }

                log_tool_call(
                    tool_name=step.name,
                    arguments=step.arguments,
                    result=result,
                    status="error",
                    ticket_id=ticket_id,
                    agent_run_id=agent_run_id,
                )

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
            final_response = (
                interaction.output_text
                or "The agent could not execute any tool calls."
            )

            complete_agent_run(
                run_id=agent_run_id,
                final_response=final_response,
                status="completed",
                ticket_id=run_ticket_id,
            )

            return final_response

        try:
            interaction = client.interactions.create(
                model="gemini-3.6-flash",
                previous_interaction_id=interaction.id,
                tools=AGENT_TOOLS,
                input=function_results,
            )

        except Exception:
            fail_agent_run(
                run_id=agent_run_id,
                final_response="Agent execution failed.",
            )

            raise

    final_response = (
        "Agent stopped after reaching the maximum number of steps."
    )

    complete_agent_run(
        run_id=agent_run_id,
        final_response=final_response,
        status="completed",
        ticket_id=run_ticket_id,
    )

    return final_response