from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    message: Mapped[str] = mapped_column(Text)

    status: Mapped[str] = mapped_column(
        String(50),
        default="new",
    )

    # nullable=True
    # Allows ticket creation if AI service is unavailable
    category: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    priority: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    customer_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
