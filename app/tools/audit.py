from app.db.database import SessionLocal
from app.db.models import AgentToolCall


def log_tool_call(
    tool_name: str,
    arguments: dict,
    result,
    status: str,
    ticket_id: int | None = None,
    agent_run_id: int | None = None,
) -> None:
    with SessionLocal() as session:
        tool_call = AgentToolCall(
            ticket_id=ticket_id,
            tool_name=tool_name,
            arguments=arguments,
            result=result,
            status=status,
        )

        session.add(tool_call)
        session.commit()