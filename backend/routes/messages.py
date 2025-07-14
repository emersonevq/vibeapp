from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from main import get_db, get_current_user, User, Message, MessageCreate, MessageResponse, Conversation

router = APIRouter()

@router.post("/", response_model=MessageResponse)
def send_message(message: MessageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Check if receiver exists
    receiver = db.query(User).filter(User.id == message.receiver_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")
    
    # Can't send message to yourself
    if current_user.id == message.receiver_id:
        raise HTTPException(status_code=400, detail="Cannot send message to yourself")
    
    db_message = Message(
        sender_id=current_user.id,
        receiver_id=message.receiver_id,
        content=message.content,
        message_type=message.message_type,
        media_url=message.media_url
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    # Update or create conversation
    conversation = db.query(Conversation).filter(
        ((Conversation.user1_id == current_user.id) & (Conversation.user2_id == message.receiver_id)) |
        ((Conversation.user1_id == message.receiver_id) & (Conversation.user2_id == current_user.id))
    ).first()
    
    if not conversation:
        conversation = Conversation(
            user1_id=current_user.id,
            user2_id=message.receiver_id,
            last_message_id=db_message.id
        )
        db.add(conversation)
    else:
        conversation.last_message_id = db_message.id
    
    db.commit()
    
    return db_message

@router.get("/conversation/{user_id}", response_model=List[MessageResponse])
def get_conversation(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    messages = db.query(Message).filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.created_at.asc()).all()
    
    return messages

@router.get("/conversations")
def get_conversations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conversations = db.query(Conversation).filter(
        (Conversation.user1_id == current_user.id) | (Conversation.user2_id == current_user.id)
    ).all()
    
    return conversations

@router.put("/{message_id}/read")
def mark_as_read(message_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.receiver_id == current_user.id
    ).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    message.is_read = True
    db.commit()
    
    return {"message": "Message marked as read"}