from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from main import (
    get_db, get_current_user, User, Share, ShareCreate, Post
)

router = APIRouter()

@router.post("/")
def share_post(share: ShareCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if post exists
    post = db.query(Post).filter(Post.id == share.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if user already shared this post
    existing_share = db.query(Share).filter(
        Share.user_id == current_user.id,
        Share.post_id == share.post_id
    ).first()
    
    if existing_share:
        raise HTTPException(status_code=400, detail="Post already shared")
    
    db_share = Share(
        user_id=current_user.id,
        post_id=share.post_id
    )
    db.add(db_share)
    db.commit()
    
    return {"message": "Post shared successfully"}

@router.delete("/{post_id}")
def unshare_post(post_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    share = db.query(Share).filter(
        Share.user_id == current_user.id,
        Share.post_id == post_id
    ).first()
    
    if not share:
        raise HTTPException(status_code=404, detail="Share not found")
    
    db.delete(share)
    db.commit()
    
    return {"message": "Post unshared successfully"}