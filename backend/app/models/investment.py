import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, UUID
from sqlalchemy.orm import relationship

from app.database.database import Base


class Investment(Base):
    __tablename__ = "investments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String, nullable=False)
    name = Column(String, nullable=False)
    quantity = Column(Numeric(10, 4), nullable=False)
    avg_buy_price = Column(Numeric(12, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="investments")

    def __repr__(self):
        return f"<Investment(id={self.id}, symbol='{self.symbol}', quantity={self.quantity}, user_id={self.user_id})>"
