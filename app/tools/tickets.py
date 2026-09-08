from sqlalchemy import select

from app.db.database import SessionLocal
from app.db.models import Ticket
from app.schemas import TicketClassification

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

def create_ticket_record(message: str) -> Ticket:
    with SessionLocal() as session:
        ticket = Ticket(
            message=message,
            status="new",
        )

        session.add(ticket)
        session.commit()
        session.refresh(ticket)

        return ticket


def classify_ticket_record(
    ticket_id: int,
    classification: TicketClassification,
) -> Ticket | None:
    with SessionLocal() as session:
        ticket = session.scalar(
            select(Ticket).where(
                Ticket.id == ticket_id
            )
        )

        if ticket is None:
            return None

        ticket.category = classification.category.value
        ticket.priority = classification.priority.value
        ticket.customer_id = classification.customer_id
        ticket.summary = classification.summary
        ticket.status = "classified"

        session.commit()
        session.refresh(ticket)

        return ticket


def mark_ticket_classification_failed(
    ticket_id: int,
) -> Ticket | None:
    with SessionLocal() as session:
        ticket = session.scalar(
            select(Ticket).where(
                Ticket.id == ticket_id
            )
        )

        if ticket is None:
            return None

        ticket.status = "classification_failed"

        session.commit()
        session.refresh(ticket)

        return ticket