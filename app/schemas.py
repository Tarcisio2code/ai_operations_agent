from enum import Enum

from pydantic import BaseModel, Field

class TicketCreate(BaseModel):
    message: str = Field(
        min_length=10,
        max_length=2000,
        examples=[
            "Customer 3821 completed an offer but did not receive the reward."
        ],
    )

class TicketCategory(str, Enum):
    MISSING_REWARD = "missing_reward"
    ACCOUNT_ISSUE = "account_issue"
    PAYMENT_ISSUE= "payment_issue"
    TECHNICAL_ISSUE = "technical_issue"
    OTHER = "other"

class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TicketClassification(BaseModel):
    category: TicketCategory
    priority: TicketPriority
    customer_id: int | None = None
    summary: str = Field(
        min_length=5,
        max_length=300,
    )

class TicketResponse(BaseModel):
    id: int
    message: str
    status: str
    category: TicketCategory | None = None
    priority: TicketPriority | None = None
    customer_id: int | None = None
    summary: str | None = None