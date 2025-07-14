from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from main import get_db, get_current_user, User, Comment, CommentCreate, CommentResponse, Post

router = APIRouter()

@router.post("/", response_model=CommentResponse)
def create_comment(comment: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Check if post exists
    post = db.query(Post).filter(Post.id == comment.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    db_comment = Comment(
        content=comment.content,
        post_id=comment.post_id,
        parent_id=comment.parent_id,
        author_id=current_user.id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    db_comment.reactions_count = 0
    db_comment.replies = []
    
    return db_comment

@router.get("/post/{post_id}", response_model=List[CommentResponse])
def get_post_comments(post_id: int, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.post_id == post_id, Comment.parent_id.is_(None)).all()
    for comment in comments:
        comment.reactions_count = 0
        comment.replies = db.query(Comment).filter(Comment.parent_id == comment.id).all()
        for reply in comment.replies:
            reply.reactions_count = 0
    return comments

@router.delete("/{comment_id}")
def delete_comment(comment_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    
    db.delete(comment)
    db.commit()
    
    return {"message": "Comment deleted successfully"}