from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from main import get_db, get_current_user, User, Friendship, FriendshipCreate, FriendshipResponse

router = APIRouter()

@router.post("/", response_model=FriendshipResponse)
def send_friend_request(friendship: FriendshipCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Check if user exists
    addressee = db.query(User).filter(User.id == friendship.addressee_id).first()
    if not addressee:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Can't send request to yourself
    if current_user.id == friendship.addressee_id:
        raise HTTPException(status_code=400, detail="Cannot send friend request to yourself")
    
    # Check if friendship already exists
    existing_friendship = db.query(Friendship).filter(
        ((Friendship.requester_id == current_user.id) & (Friendship.addressee_id == friendship.addressee_id)) |
        ((Friendship.requester_id == friendship.addressee_id) & (Friendship.addressee_id == current_user.id))
    ).first()
    
    if existing_friendship:
        raise HTTPException(status_code=400, detail="Friendship request already exists")
    
    db_friendship = Friendship(
        requester_id=current_user.id,
        addressee_id=friendship.addressee_id,
        status="pending"
    )
    db.add(db_friendship)
    db.commit()
    db.refresh(db_friendship)
    
    return db_friendship

@router.get("/pending", response_model=List[FriendshipResponse])
def get_pending_requests(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    friendships = db.query(Friendship).filter(
        Friendship.addressee_id == current_user.id,
        Friendship.status == "pending"
    ).all()
    
    return friendships

@router.put("/{friendship_id}/accept")
def accept_friend_request(friendship_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    friendship = db.query(Friendship).filter(
        Friendship.id == friendship_id,
        Friendship.addressee_id == current_user.id,
        Friendship.status == "pending"
    ).first()
    
    if not friendship:
        raise HTTPException(status_code=404, detail="Friend request not found")
    
    friendship.status = "accepted"
    db.commit()
    
    return {"message": "Friend request accepted"}

@router.put("/{friendship_id}/reject")
def reject_friend_request(friendship_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    friendship = db.query(Friendship).filter(
        Friendship.id == friendship_id,
        Friendship.addressee_id == current_user.id,
        Friendship.status == "pending"
    ).first()
    
    if not friendship:
        raise HTTPException(status_code=404, detail="Friend request not found")
    
    db.delete(friendship)
    db.commit()
    
    return {"message": "Friend request rejected"}

@router.get("/", response_model=List[FriendshipResponse])
def get_friends(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    friendships = db.query(Friendship).filter(
        ((Friendship.requester_id == current_user.id) | (Friendship.addressee_id == current_user.id)) &
        (Friendship.status == "accepted")
    ).all()
    
    return friendships