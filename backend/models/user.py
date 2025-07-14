from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from models.base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    # ... outros campos do usuário
    
    # Relacionamentos
    notifications_received = relationship("Notification", foreign_keys="[Notification.recipient_id]", back_populates="recipient")
    notifications_sent = relationship("Notification", foreign_keys="[Notification.sender_id]", back_populates="sender")