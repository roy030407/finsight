import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UUID
from sqlalchemy.orm import relationship

from app.database.database import Base


class BlockchainLedger(Base):
    __tablename__ = "blockchain_ledger"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=False)
    block_index = Column(Integer, nullable=False)
    previous_hash = Column(String, nullable=False)
    current_hash = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    nonce = Column(Integer, nullable=False)

    transaction = relationship("Transaction", back_populates="blockchain_ledger")

    def __repr__(self):
        return f"<BlockchainLedger(id={self.id}, transaction_id={self.transaction_id}, block_index={self.block_index})>"
