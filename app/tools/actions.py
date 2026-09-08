from sqlalchemy import select

from app.db.database import SessionLocal
from app.db.models import ProposedAction, Ticket
from app.tools.tickets import escalate_case

def propose_escalation(
    ticket_id: int,
    reason: str,
) -> dict | None:
    with SessionLocal() as session:
        ticket = session.scalar(
            select(Ticket).where(Ticket.id == ticket_id)
        )

        if ticket is None:
            return None

        action = ProposedAction(
            ticket_id=ticket_id,
            action_type="escalate_case",
            reason=reason,
            status="pending",
        )

        session.add(action)
        session.commit()
        session.refresh(action)

        return {
            "id": action.id,
            "ticket_id": action.ticket_id,
            "action_type": action.action_type,
            "reason": action.reason,
            "status": action.status,
        }

def approve_action(action_id: int) -> dict | None:
    with SessionLocal() as session:
        action = session.scalar(
            select(ProposedAction).where(
                ProposedAction.id == action_id
            )
        )

        if action is None:
            return None

        if action.status != "pending":
            return {
                "id": action.id,
                "ticket_id": action.ticket_id,
                "action_type": action.action_type,
                "reason": action.reason,
                "status": action.status,
            }

        if action.action_type == "escalate_case":
            result = escalate_case(
                ticket_id=action.ticket_id,
                reason=action.reason,
            )

            if result is None:
                return None

        action.status = "approved"

        session.commit()
        session.refresh(action)

        return {
            "id": action.id,
            "ticket_id": action.ticket_id,
            "action_type": action.action_type,
            "reason": action.reason,
            "status": action.status,
        }

def reject_action(action_id: int) -> dict | None:
    with SessionLocal() as session:
        action = session.scalar(
            select(ProposedAction).where(
                ProposedAction.id == action_id
            )
        )

        if action is None:
            return None

        if action.status != "pending":
            return {
                "id": action.id,
                "ticket_id": action.ticket_id,
                "action_type": action.action_type,
                "reason": action.reason,
                "status": action.status,
            }

        action.status = "rejected"

        session.commit()
        session.refresh(action)

        return {
            "id": action.id,
            "ticket_id": action.ticket_id,
            "action_type": action.action_type,
            "reason": action.reason,
            "status": action.status,
        }