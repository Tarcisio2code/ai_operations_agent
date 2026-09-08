from fastapi import FastAPI, HTTPException

from app.schemas import (
    ActionProposalCreate,
    ActionProposalResponse,
    AgentRequest,
    AgentResponse,
    TicketClassification,
    TicketCreate,
    TicketResponse,
    ActionDetailResponse,
    AgentRunResponse,
    AgentToolCallResponse,
    TicketDetailResponse,
)

from app.services.llm import classify_ticket

from app.db.database import SessionLocal
from app.db.models import Ticket

from app.agent.operations import run_agent

from app.tools.actions import approve_action, propose_escalation, reject_action

from app.tools.queries import (
    get_agent_runs,
    get_ticket,
    get_ticket_actions,
    get_ticket_tool_calls,
    get_agent_run,
    get_agent_run_tool_calls,
)

from app.tools.tickets import (
    classify_ticket_record,
    create_ticket_record,
    mark_ticket_classification_failed,
)

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
    db_ticket = create_ticket_record(
        ticket.message
    )

    try:
        classification = classify_ticket(
            ticket.message
        )
    except Exception:
        mark_ticket_classification_failed(
            db_ticket.id
        )

        raise HTTPException(
            status_code=503,
            detail=(
                "Ticket was created, but AI "
                "classification is temporarily unavailable."
            ),
        )

    try:
        db_ticket = classify_ticket_record(
            db_ticket.id,
            classification,
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=(
                "Ticket was created, but its "
                "classification could not be saved."
            ),
        )

    if db_ticket is None:
        raise HTTPException(
            status_code=500,
            detail=(
                "Ticket was created, but its "
                "classification could not be saved."
            ),
        )

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
    try:
        response = run_agent(request.message)

    except Exception:
        raise HTTPException(
            status_code=503,
            detail=(
                "The AI agent is temporarily unavailable. "
                "Please try again later."
            ),
        )

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

    if action is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found.",
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
        reason=action["reason"],
        status=action["status"],
    )

@app.post(
    "/actions/{action_id}/reject",
    response_model=ActionProposalResponse,
)
def reject_action_endpoint(action_id: int):
    action = reject_action(action_id)

    if action is None:
        raise HTTPException(
            status_code=404,
            detail="Action not found.",
        )

    return ActionProposalResponse(
        id=action["id"],
        ticket_id=action["ticket_id"],
        action_type=action["action_type"],
        reason=action["reason"],
        status=action["status"],
    )

@app.get(
    "/tickets/{ticket_id}",
    response_model=TicketDetailResponse,
)
def get_ticket_endpoint(ticket_id: int):
    ticket = get_ticket(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found.",
        )

    return TicketDetailResponse(
        id=ticket.id,
        message=ticket.message,
        status=ticket.status,
        category=ticket.category,
        priority=ticket.priority,
        customer_id=ticket.customer_id,
        summary=ticket.summary,
        escalation_reason=ticket.escalation_reason,
    )

@app.get(
    "/tickets/{ticket_id}/actions",
    response_model=list[ActionDetailResponse],
)
def get_ticket_actions_endpoint(ticket_id: int):
    ticket = get_ticket(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found.",
        )

    actions = get_ticket_actions(ticket_id)

    return [
        ActionDetailResponse(
            id=action.id,
            ticket_id=action.ticket_id,
            action_type=action.action_type,
            reason=action.reason,
            status=action.status,
        )
        for action in actions
    ]

@app.get(
    "/tickets/{ticket_id}/tool-calls",
    response_model=list[AgentToolCallResponse],
)
def get_ticket_tool_calls_endpoint(ticket_id: int):
    ticket = get_ticket(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found.",
        )

    tool_calls = get_ticket_tool_calls(ticket_id)

    return [
        AgentToolCallResponse(
            id=tool_call.id,
            ticket_id=tool_call.ticket_id,
            tool_name=tool_call.tool_name,
            arguments=tool_call.arguments,
            result=tool_call.result,
            status=tool_call.status,
            agent_run_id=tool_call.agent_run_id,
        )
        for tool_call in tool_calls
    ]

@app.get(
    "/agent-runs",
    response_model=list[AgentRunResponse],
)
def get_agent_runs_endpoint():
    runs = get_agent_runs()

    return [
        AgentRunResponse(
            id=run.id,
            ticket_id=run.ticket_id,
            user_message=run.user_message,
            final_response=run.final_response,
            status=run.status,
        )
        for run in runs
    ]

@app.get(
    "/agent-runs/{run_id}",
    response_model=AgentRunResponse,
)
def get_agent_run_endpoint(run_id: int):
    run = get_agent_run(run_id)

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Agent run not found.",
        )

    return AgentRunResponse(
        id=run.id,
        ticket_id=run.ticket_id,
        user_message=run.user_message,
        final_response=run.final_response,
        status=run.status,
    )

@app.get(
    "/agent-runs/{run_id}/tool-calls",
    response_model=list[AgentToolCallResponse],
)
def get_agent_run_tool_calls_endpoint(
    run_id: int,
):
    run = get_agent_run(run_id)

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Agent run not found.",
        )

    tool_calls = get_agent_run_tool_calls(
        run_id
    )

    return [
        AgentToolCallResponse(
            id=tool_call.id,
            agent_run_id=tool_call.agent_run_id,
            ticket_id=tool_call.ticket_id,
            tool_name=tool_call.tool_name,
            arguments=tool_call.arguments,
            result=tool_call.result,
            status=tool_call.status,
        )
        for tool_call in tool_calls
    ]


