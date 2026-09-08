from sqlalchemy import select

from app.db.database import SessionLocal
from app.db.models import AgentRun

def create_agent_run(
    user_message: str,
    ticket_id: int | None = None,
) -> int:
    with SessionLocal() as session:
        run = AgentRun(
            ticket_id=ticket_id,
            user_message=user_message,
            final_response=None,
            status="running",
        )

        session.add(run)
        session.commit()
        session.refresh(run)

        return run.id

def complete_agent_run(
    run_id: int,
    final_response: str,
    status: str,
    ticket_id: int | None = None,
) -> None:
    with SessionLocal() as session:
        run = session.scalar(
            select(AgentRun).where(
                AgentRun.id == run_id
            )
        )

        if run is None:
            return

        run.final_response = final_response
        run.status = status

        if ticket_id is not None:
            run.ticket_id = ticket_id

        session.commit()

def fail_agent_run(
    run_id: int,
    final_response: str,
) -> None:
    with SessionLocal() as session:
        run = session.scalar(
            select(AgentRun).where(
                AgentRun.id == run_id
            )
        )

        if run is None:
            return

        run.final_response = final_response
        run.status = "failed"

        session.commit()
