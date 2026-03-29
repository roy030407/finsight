import enum
import uuid
from datetime import datetime, date

from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, UUID
from sqlalchemy.orm import relationship

from app.database.database import Base


class TransactionType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    category = Column(String, nullable=False)
    description = Column(String, nullable=True)
    date = Column(Date, nullable=False)
    payment_mode = Column(String, nullable=True)
    account = Column(String, nullable=True)
    blockchain_hash = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="transactions")
    blockchain_ledger = relationship(
        "BlockchainLedger", back_populates="transaction", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Transaction(id={self.id}, amount={self.amount}, type='{self.type.value}', user_id={self.user_id})>"
