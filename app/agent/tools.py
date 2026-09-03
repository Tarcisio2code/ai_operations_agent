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

AGENT_TOOLS = [
    GET_CUSTOMER_TOOL,
    GET_TRANSACTIONS_TOOL,
]