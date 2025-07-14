from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from main import get_db, get_current_user, User, Follow, FollowCreate

router = APIRouter()

@router.post("/")
def follow_user(follow: FollowCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Check if user exists
    followed_user = db.query(User).filter(User.id == follow.followed_id).first()
    if not followed_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Can't follow yourself
    if current_user.id == follow.followed_id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    
    # Check if already following
    existing_follow = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.followed_id == follow.followed_id
    ).first()
    
    if existing_follow:
        # Unfollow
        db.delete(existing_follow)
        db.commit()
        return {"message": "User unfollowed"}
    
    # Follow
    db_follow = Follow(
        follower_id=current_user.id,
        followed_id=follow.followed_id
    )
    db.add(db_follow)
    db.commit()
    
    return {"message": "User followed"}

@router.get("/followers/{user_id}")
def get_followers(user_id: int, db: Session = Depends(get_db)):
    followers = db.query(Follow).filter(Follow.followed_id == user_id).all()
    return {"followers": followers, "count": len(followers)}

@router.get("/following/{user_id}")
def get_following(user_id: int, db: Session = Depends(get_db)):
    following = db.query(Follow).filter(Follow.follower_id == user_id).all()
    return {"following": following, "count": len(following)}

@router.get("/status/{user_id}")
def get_follow_status(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    follow = db.query(Follow).filter(
        Follow.follower_id == current_user.id,
        Follow.followed_id == user_id
    ).first()
    
    return {"is_following": follow is not None}