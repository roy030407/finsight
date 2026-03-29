import uuid
from datetime import datetime, date

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Numeric, String, UUID
from sqlalchemy.orm import relationship

from app.database.database import Base


class Goal(Base):
    __tablename__ = "goals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    target_amount = Column(Numeric(12, 2), nullable=False)
    current_amount = Column(Numeric(12, 2), default=0, nullable=False)
    deadline = Column(Date, nullable=True)
    icon = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="goals")

    def __repr__(self):
        return f"<Goal(id={self.id}, title='{self.title}', target_amount={self.target_amount}, user_id={self.user_id})>"
