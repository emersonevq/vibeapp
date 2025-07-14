from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from main import get_db, get_current_user, User, Story, StoryCreate, StoryResponse, StoryView
import base64
import os

router = APIRouter()

@router.post("/", response_model=StoryResponse)
def create_story(story: StoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Handle base64 media data
    media_url = story.media_url
    if media_url and media_url.startswith('data:'):
        # Extract base64 data and save as file
        try:
            header, data = media_url.split(',', 1)
            file_data = base64.b64decode(data)
            
            # Create uploads directory if it doesn't exist
            os.makedirs('uploads/stories', exist_ok=True)
            
            # Generate filename
            file_extension = 'jpg' if 'image' in header else 'mp4' if 'video' in header else 'mp3'
            filename = f"story_{current_user.id}_{int(datetime.utcnow().timestamp())}.{file_extension}"
            file_path = f"uploads/stories/{filename}"
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            media_url = f"http://localhost:8000/{file_path}"
        except Exception as e:
            print(f"Error saving media file: {e}")
            media_url = None
    
    expires_at = datetime.utcnow() + timedelta(hours=story.duration_hours)
    
    db_story = Story(
        content=story.content,
        media_type=story.media_type,
        media_url=media_url,
        background_color=story.background_color,
        duration_hours=story.duration_hours,
        author_id=current_user.id,
        expires_at=expires_at
    )
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    
    db_story.views_count = 0
    return db_story

@router.get("/", response_model=List[StoryResponse])
def get_active_stories(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    stories = db.query(Story).filter(Story.expires_at > now).order_by(Story.created_at.desc()).all()
    
    for story in stories:
        story.views_count = db.query(StoryView).filter(StoryView.story_id == story.id).count()
    
    return stories

@router.post("/{story_id}/view")
def view_story(story_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    if story.expires_at <= datetime.utcnow():
        raise HTTPException(status_code=410, detail="Story has expired")
    
    # Check if already viewed
    existing_view = db.query(StoryView).filter(
        StoryView.story_id == story_id,
        StoryView.viewer_id == current_user.id
    ).first()
    
    if not existing_view:
        db_view = StoryView(
            story_id=story_id,
            viewer_id=current_user.id
        )
        db.add(db_view)
        db.commit()
    
    return {"message": "Story viewed"}

@router.delete("/{story_id}")
def delete_story(story_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    if story.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this story")
    
    # Delete associated file if exists
    if story.media_url and story.media_url.startswith('http://localhost:8000/uploads/'):
        file_path = story.media_url.replace('http://localhost:8000/', '')
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file: {e}")
    
    db.delete(story)
    db.commit()
    
    return {"message": "Story deleted successfully"}