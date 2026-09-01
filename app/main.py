from fastapi import FastAPI

from app.schemas import TicketCreate, TicketResponse

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
    return TicketResponse(
        id=1,
        message=ticket.message,
        status="new",
    )
