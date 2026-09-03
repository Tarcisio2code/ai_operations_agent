from sqlalchemy import select

from app.db.database import SessionLocal
from app.db.models import Transaction


def get_transactions(customer_id: int) -> list[dict]:
    with SessionLocal() as session:
        transactions = session.scalars(
            select(Transaction).where(
                Transaction.customer_id == customer_id
            )
        ).all()

        return [
            {
                "id": transaction.id,
                "customer_id": transaction.customer_id,
                "offer_id": transaction.offer_id,
                "amount": float(transaction.amount),
                "status": transaction.status,
            }
            for transaction in transactions
        ]