GET_CUSTOMER_TOOL = {
    "type": "function",
    "name": "get_customer",
    "description": "Get customer information from the database using a customer ID.",
    "parameters": {
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "integer",
                "description": "The unique ID of the customer.",
            }
        },
        "required": ["customer_id"],
    },
}

GET_TRANSACTIONS_TOOL = {
    "type": "function",
    "name": "get_transactions",
    "description": "Get all transactions associated with a customer ID.",
    "parameters": {
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "integer",
                "description": "The unique ID of the customer.",
            }
        },
        "required": ["customer_id"],
    },
}

PROPOSE_ESCALATION_TOOL = {
    "type": "function",
    "name": "propose_escalation",
    "description": (
        "Propose that a support ticket be escalated for human review. "
        "This creates a pending action and does not execute the escalation."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "ticket_id": {
                "type": "integer",
                "description": "The ID of the support ticket.",
            },
            "reason": {
                "type": "string",
                "description": (
                    "A concise explanation of why the ticket "
                    "should be escalated."
                ),
            },
        },
        "required": [
            "ticket_id",
            "reason",
        ],
    },
}

AGENT_TOOLS = [
    GET_CUSTOMER_TOOL,
    GET_TRANSACTIONS_TOOL,
    PROPOSE_ESCALATION_TOOL,
]
