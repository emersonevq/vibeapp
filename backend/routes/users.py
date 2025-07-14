from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from main import (
    get_db, get_current_user, User, UserResponse, Post, PostResponse,
    Reaction, Comment, Share, Friendship
)

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 20, search: str = "", db: Session = Depends(get_db)):
    query = db.query(User).filter(User.is_active == True)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (User.first_name.ilike(search_filter)) |
            (User.last_name.ilike(search_filter)) |
            (User.email.ilike(search_filter)) |
            (User.phone.ilike(search_filter))
        )
    
    users = query.offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/{user_id}/posts", response_model=List[PostResponse])
def get_user_posts(user_id: int, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    posts = db.query(Post).filter(Post.author_id == user_id).order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
    
    # Add counts for each post
    for post in posts:
        post.reactions_count = db.query(Reaction).filter(Reaction.post_id == post.id).count()
        post.comments_count = db.query(Comment).filter(Comment.post_id == post.id).count()
        post.shares_count = db.query(Share).filter(Share.post_id == post.id).count()
    
    return posts

@router.get("/{user_id}/testimonials", response_model=List[PostResponse])
def get_user_testimonials(user_id: int, skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    posts = db.query(Post).filter(
        Post.post_type == "testimonial"
    ).order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
    
    # Add counts for each post
    for post in posts:
        post.reactions_count = db.query(Reaction).filter(Reaction.post_id == post.id).count()
        post.comments_count = db.query(Comment).filter(Comment.post_id == post.id).count()
        post.shares_count = db.query(Share).filter(Share.post_id == post.id).count()
    
    return posts

@router.get("/{user_id}/stats")
def get_user_stats(user_id: int, db: Session = Depends(get_db)):
    # Count posts
    posts_count = db.query(Post).filter(Post.author_id == user_id).count()
    
    # Count friends
    friends_count = db.query(Friendship).filter(
        ((Friendship.requester_id == user_id) | (Friendship.addressee_id == user_id)) &
        (Friendship.status == "accepted")
    ).count()
    
    # Count testimonials
    testimonials_count = db.query(Post).filter(
        Post.post_type == "testimonial"
    ).count()
    
    # Count total likes received
    likes_count = db.query(Reaction).join(Post).filter(
        Post.author_id == user_id,
        Reaction.reaction_type == "like"
    ).count()
    
    return {
        "posts_count": posts_count,
        "friends_count": friends_count,
        "testimonials_count": testimonials_count,
        "likes_count": likes_count
    }