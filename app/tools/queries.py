from sqlalchemy import select

from app.db.database import SessionLocal
from app.db.models import (
    AgentRun,
    AgentToolCall,
    ProposedAction,
    Ticket,
)


def get_ticket(ticket_id: int) -> Ticket | None:
    with SessionLocal() as session:
        return session.scalar(
            select(Ticket).where(Ticket.id == ticket_id)
        )


def get_ticket_actions(ticket_id: int) -> list[ProposedAction]:
    with SessionLocal() as session:
        return list(
            session.scalars(
                select(ProposedAction).where(
                    ProposedAction.ticket_id == ticket_id
                )
            ).all()
        )


def get_ticket_tool_calls(ticket_id: int) -> list[AgentToolCall]:
    with SessionLocal() as session:
        return list(
            session.scalars(
                select(AgentToolCall).where(
                    AgentToolCall.ticket_id == ticket_id
                )
            ).all()
        )


def get_agent_runs() -> list[AgentRun]:
    with SessionLocal() as session:
        return list(
            session.scalars(
                select(AgentRun).order_by(
                    AgentRun.created_at.desc()
                )
            ).all()
        )
