from sqlalchemy import select

from app.db.database import SessionLocal
from app.db.models import Customer, Transaction


CUSTOMERS = [
    Customer(
        id=3821,
        name="Bianca",
        email="bianca@jmail.com",
        status="active",
    ),
    Customer(
        id=4102,
        name="Elisa",
        email="elisa@jmail.com",
        status="active",
    ),
    Customer(
        id=5230,
        name="Tarcisio",
        email="tarcisio@jmail.com",
        status="suspended",
    ),
]

TRANSACTIONS = [
    Transaction(
        id=1001,
        customer_id=3821,
        offer_id="offer-apple-01",
        amount=25.00,
        status="completed",
    ),
    Transaction(
        id=1002,
        customer_id=3821,
        offer_id="offer-game-04",
        amount=10.00,
        status="pending",
    ),
    Transaction(
        id=1003,
        customer_id=4102,
        offer_id="offer-survey-02",
        amount=5.00,
        status="completed",
    ),
]

def seed_database() -> None:
    with SessionLocal() as session:
        existing_customer = session.scalar(
            select(Customer.id).limit(1)
        )

        if existing_customer is None:
            session.add_all(CUSTOMERS)
            session.commit()
            print(f"Inserted {len(CUSTOMERS)} customers.")
        else:
            print("Customers already exist. Skipping.")

        existing_transaction = session.scalar(
            select(Transaction.id).limit(1)
        )

        if existing_transaction is None:
            session.add_all(TRANSACTIONS)
            session.commit()
            print(f"Inserted {len(TRANSACTIONS)} transactions.")
        else:
            print("Transactions already exist. Skipping.")


if __name__ == "__main__":
    seed_database()
