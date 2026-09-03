from sqlalchemy import select

from app.db.database import SessionLocal
from app.db.models import Customer


def get_customer(customer_id: int) -> dict | None:
    with SessionLocal() as session:
        customer = session.scalar(
            select(Customer).where(Customer.id == customer_id)
        )

        if customer is None:
            return None

        return {
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
            "status": customer.status,
        }