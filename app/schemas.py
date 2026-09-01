from pydantic import BaseModel, Field


class TicketCreate(BaseModel):
    message: str = Field(
        min_length=10,
        max_length=2000,
        examples=[
            "Customer 3821 completed an offer but did not receive the reward."
        ],
    )


class TicketResponse(BaseModel):
    id: int
    message: str
    status: str
