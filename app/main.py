from fastapi import FastAPI, HTTPException

from app.schemas import (
    ActionProposalCreate,
    ActionProposalResponse,
    AgentRequest,
    AgentResponse,
    TicketClassification,
    TicketCreate,
    TicketResponse,
)

from app.services.llm import classify_ticket

from app.db.database import SessionLocal
from app.db.models import Ticket

from app.agent.operations import run_agent

from app.tools.actions import approve_action, propose_escalation

app = FastAPI(
	title="AI Operation Agent",
	description="LLM-powered operations workflow agent.",
	version="0.1.0",
)

@app.get("/health")
async def health_check():
	return {"status": "ok"}

@app.post(
    "/tickets",
    response_model=TicketResponse,
    status_code=201,
)
def create_ticket(ticket: TicketCreate):
    classification = classify_ticket(ticket.message)

    db_ticket = Ticket(
        message=ticket.message,
        status="classified",
        category=classification.category.value,
        priority=classification.priority.value,
        customer_id=classification.customer_id,
        summary=classification.summary,
    )

    with SessionLocal() as session:
        session.add(db_ticket)
        session.commit()
        session.refresh(db_ticket)

    return TicketResponse(
        id=db_ticket.id,
        message=db_ticket.message,
        status=db_ticket.status,
        category=db_ticket.category,
        priority=db_ticket.priority,
        customer_id=db_ticket.customer_id,
        summary=db_ticket.summary,
    )

@app.post(
    "/tickets/classify",
    response_model=TicketClassification,
)
async def classify_ticket_endpoint(ticket: TicketCreate):
    return classify_ticket(ticket.message)

@app.post(
    "/agent",
    response_model=AgentResponse,
)
def agent(request: AgentRequest):
    response = run_agent(request.message)

    return AgentResponse(
        response=response,
    )

@app.post(
    "/actions",
    response_model=ActionProposalResponse,
    status_code=201,
)
def create_action_proposal(
    request: ActionProposalCreate,
):
    action = propose_escalation(
        ticket_id=request.ticket_id,
        reason=request.reason,
    )

    return ActionProposalResponse(
        id=action["id"],
        ticket_id=action["ticket_id"],
        action_type=action["action_type"],
        reason=action["reason"],
        status=action["status"],
    )

@app.post(
    "/actions/{action_id}/approve",
    response_model=ActionProposalResponse,
)
def approve_action_endpoint(action_id: int):
    action = approve_action(action_id)

    if action is None:
        raise HTTPException(
            status_code=404,
            detail="Action not found or could not be executed.",
        )

    return ActionProposalResponse(
        id=action["id"],
        ticket_id=action["ticket_id"],
        action_type=action["action_type"],
        status=action["status"],
    )