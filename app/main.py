from fastapi import FastAPI

from app.schemas import TicketCreate, TicketResponse
from app.schemas import TicketClassification

from app.services.llm import classify_ticket

from app.db.database import SessionLocal
from app.db.models import Ticket

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
