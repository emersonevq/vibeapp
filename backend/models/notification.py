from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base  # Importe Base de um arquivo centralizado

class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = {'extend_existing': True}  # Permite redefinição segura
    
    id = Column(Integer, primary_key=True, index=True)
    recipient_id = Column(Integer, ForeignKey("users.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String)  # Pode usar Enum se preferir
    title = Column(String)
    message = Column(Text)
    data = Column(Text, nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    recipient = relationship("User", foreign_keys=[recipient_id])
    sender = relationship("User", foreign_keys=[sender_id])