from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from main import (
    get_db, get_current_user, User, Like, LikeCreate, Post
)

router = APIRouter()

@router.post("/")
def toggle_like(like: LikeCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if post exists
    post = db.query(Post).filter(Post.id == like.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if user already liked this post
    existing_like = db.query(Like).filter(
        Like.user_id == current_user.id,
        Like.post_id == like.post_id
    ).first()
    
    if existing_like:
        # Remove like
        db.delete(existing_like)
        db.commit()
        return {"message": "Like removed"}
    else:
        # Add like
        db_like = Like(
            user_id=current_user.id,
            post_id=like.post_id
        )
        db.add(db_like)
        db.commit()
        return {"message": "Post liked"}

@router.get("/post/{post_id}")
def get_like_status(post_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    like = db.query(Like).filter(
        Like.user_id == current_user.id,
        Like.post_id == post_id
    ).first()
    
    total_likes = db.query(Like).filter(Like.post_id == post_id).count()
    
    return {
        "has_liked": like is not None,
        "total_likes": total_likes
    }

@router.delete("/{post_id}")
def unlike_post(post_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    like = db.query(Like).filter(
        Like.user_id == current_user.id,
        Like.post_id == post_id
    ).first()
    
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")
    
    db.delete(like)
    db.commit()
    
    return {"message": "Post unliked"}