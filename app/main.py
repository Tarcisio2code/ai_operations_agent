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
async def create_ticket(ticket: TicketCreate):
    db_ticket = Ticket(
        message=ticket.message,
    )

    with SessionLocal() as session:
        session.add(db_ticket)
        session.commit()
        session.refresh(db_ticket)

    return TicketResponse(
        id=db_ticket.id,
        message=db_ticket.message,
        status=db_ticket.status,
    )

@app.post(
    "/tickets/classify",
    response_model=TicketClassification,
)
async def classify_ticket_endpoint(ticket: TicketCreate):
    return classify_ticket(ticket.message)
