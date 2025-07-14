from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from main import (
    get_db, get_current_user, User, Block, BlockCreate
)

router = APIRouter()

@router.post("/")
def block_user(block: BlockCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if user exists
    blocked_user = db.query(User).filter(User.id == block.blocked_id, User.is_active == True).first()
    if not blocked_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Can't block yourself
    if current_user.id == block.blocked_id:
        raise HTTPException(status_code=400, detail="Cannot block yourself")
    
    # Check if already blocked
    existing_block = db.query(Block).filter(
        Block.blocker_id == current_user.id,
        Block.blocked_id == block.blocked_id
    ).first()
    
    if existing_block:
        raise HTTPException(status_code=400, detail="User already blocked")
    
    # Create block
    db_block = Block(
        blocker_id=current_user.id,
        blocked_id=block.blocked_id
    )
    db.add(db_block)
    db.commit()
    
    return {"message": "User blocked successfully"}

@router.delete("/{block_id}")
def unblock_user(block_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    block = db.query(Block).filter(Block.id == block_id).first()
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    
    if block.blocker_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to unblock this user")
    
    db.delete(block)
    db.commit()
    
    return {"message": "User unblocked successfully"}

@router.get("/")
def get_blocked_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    blocks = db.query(Block).filter(Block.blocker_id == current_user.id).all()
    return blocks