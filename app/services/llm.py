from google import genai

from app.config import settings
from app.schemas import TicketClassification


client = genai.Client(api_key=settings.gemini_api_key)


def classify_ticket(message: str) -> TicketClassification:
    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=(
            "You classify customer support tickets for an operations team.\n"
            "Extract the customer ID only when explicitly present.\n"
            "Choose the most appropriate category and priority.\n"
            "Write a short factual summary.\n"
            "Do not invent information.\n\n"
            f"Ticket:\n{message}"
        ),
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": TicketClassification.model_json_schema(),
        },
    )

    return TicketClassification.model_validate_json(
        interaction.output_text
    )
