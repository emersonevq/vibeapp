from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from main import (
    get_db, get_current_user, User, Reaction, ReactionCreate, Post
)

router = APIRouter()

@router.post("/")
def toggle_reaction(reaction: ReactionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if post exists
    post = db.query(Post).filter(Post.id == reaction.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if user already reacted to this post
    existing_reaction = db.query(Reaction).filter(
        Reaction.user_id == current_user.id,
        Reaction.post_id == reaction.post_id
    ).first()
    
    if existing_reaction:
        if existing_reaction.reaction_type == reaction.reaction_type:
            # Remove reaction if it's the same type
            db.delete(existing_reaction)
            db.commit()
            return {"message": "Reaction removed"}
        else:
            # Update reaction type
            existing_reaction.reaction_type = reaction.reaction_type
            db.commit()
            return {"message": "Reaction updated"}
    else:
        # Add new reaction
        db_reaction = Reaction(
            user_id=current_user.id,
            post_id=reaction.post_id,
            reaction_type=reaction.reaction_type
        )
        db.add(db_reaction)
        db.commit()
        return {"message": "Reaction added"}

@router.get("/post/{post_id}")
def get_post_reactions(post_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Get user's reaction
    user_reaction = db.query(Reaction).filter(
        Reaction.user_id == current_user.id,
        Reaction.post_id == post_id
    ).first()
    
    # Get total reactions count
    total_reactions = db.query(Reaction).filter(Reaction.post_id == post_id).count()
    
    return {
        "user_reaction": user_reaction.reaction_type if user_reaction else None,
        "total": total_reactions
    }

@router.delete("/{post_id}")
def remove_reaction(post_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    reaction = db.query(Reaction).filter(
        Reaction.user_id == current_user.id,
        Reaction.post_id == post_id
    ).first()
    
    if not reaction:
        raise HTTPException(status_code=404, detail="Reaction not found")
    
    db.delete(reaction)
    db.commit()
    
    return {"message": "Reaction removed"}