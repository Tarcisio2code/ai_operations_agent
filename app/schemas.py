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

class AgentRequest(BaseModel):
    message: str = Field(
        min_length=3,
        max_length=2000,
    )

class AgentResponse(BaseModel):
    response: str

class ActionProposalCreate(BaseModel):
    ticket_id: int
    reason: str = Field(
        min_length=5,
        max_length=1000,
    )

class ActionProposalResponse(BaseModel):
    id: int
    ticket_id: int
    action_type: str
    reason: str | None = None
    status: str

class TicketDetailResponse(BaseModel):
    id: int
    message: str
    status: str
    category: TicketCategory | None = None
    priority: TicketPriority | None = None
    customer_id: int | None = None
    summary: str | None = None
    escalation_reason: str | None = None


class ActionDetailResponse(BaseModel):
    id: int
    ticket_id: int
    action_type: str
    reason: str
    status: str


class AgentToolCallResponse(BaseModel):
    id: int
    ticket_id: int | None = None
    tool_name: str
    arguments: dict
    result: dict | list | str | None = None
    status: str


class AgentRunResponse(BaseModel):
    id: int
    ticket_id: int | None = None
    user_message: str
    final_response: str | None = None
    status: str

