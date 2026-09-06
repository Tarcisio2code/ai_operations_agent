from sqlalchemy import select

from app.db.database import SessionLocal
from app.db.models import Ticket


def escalate_case(ticket_id: int, reason: str) -> dict | None:
    with SessionLocal() as session:
        ticket = session.scalar(
            select(Ticket).where(Ticket.id == ticket_id)
        )

        if ticket is None:
            return None

        ticket.status = "escalated"
        ticket.escalation_reason = reason

        session.commit()
        session.refresh(ticket)

        return {
            "id": ticket.id,
            "status": ticket.status,
            "escalation_reason": ticket.escalation_reason,
        }
