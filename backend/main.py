from fastapi import FastAPI, HTTPException, Depends, status, WebSocket, WebSocketDisconnect
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Date
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session, relationship
from datetime import datetime, timedelta, date
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, EmailStr
import os
from dotenv import load_dotenv
import json
import asyncio

# Carrega variáveis de ambiente
load_dotenv()

# Configurações
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    gender = Column(String(10))
    birth_date = Column(Date)
    phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    post_type = Column(String(20), default="post")
    media_type = Column(String(50))
    media_url = Column(String(500))
    media_metadata = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    reactions_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    
    author = relationship("User", backref="posts")

class Story(Base):
    __tablename__ = "stories"
    
    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text)
    media_type = Column(String(50))
    media_url = Column(String(500))
    background_color = Column(String(7))
    duration_hours = Column(Integer, default=24)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    views_count = Column(Integer, default=0)
    
    author = relationship("User", backref="stories")

class StoryView(Base):
    __tablename__ = "story_views"
    
    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=False)
    viewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    viewed_at = Column(DateTime, default=datetime.utcnow)
    
    story = relationship("Story", backref="views")
    viewer = relationship("User", backref="story_views")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"))
    notification_type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(Text)  # JSON data
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    recipient = relationship("User", foreign_keys=[recipient_id], backref="received_notifications")
    sender = relationship("User", foreign_keys=[sender_id], backref="sent_notifications")

class Friendship(Base):
    __tablename__ = "friendships"
    
    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    addressee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(20), default="pending")  # pending, accepted, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    requester = relationship("User", foreign_keys=[requester_id])
    addressee = relationship("User", foreign_keys=[addressee_id])

class Reaction(Base):
    __tablename__ = "reactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    reaction_type = Column(String(20), nullable=False)  # like, love, wow, angry, cute, happy
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", backref="reactions")
    post = relationship("Post", backref="reactions")

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    author = relationship("User", backref="comments")
    post = relationship("Post", backref="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies")

class Share(Base):
    __tablename__ = "shares"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", backref="shares")

# Pydantic models
class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

    def get_birth_date_as_date(self) -> Optional[date]:
        """Converte birth_date string para objeto date"""
        if self.birth_date:
            try:
                # Assume formato YYYY-MM-DD
                year, month, day = map(int, self.birth_date.split('-'))
                return date(year, month, day)
            except (ValueError, AttributeError):
                return None
        return None

class UserResponse(UserBase):
    id: int
    birth_date: Optional[Union[str, date]] = None
    is_active: bool
    created_at: datetime
    last_seen: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            date: lambda v: v.isoformat() if v else None
        }

class ReactionCreate(BaseModel):
    post_id: int
    reaction_type: str

class CommentCreate(BaseModel):
    content: str
    post_id: int
    parent_id: Optional[int] = None

class CommentResponse(BaseModel):
    id: int
    content: str
    author: Dict[str, Any]
    created_at: datetime
    reactions_count: int = 0
    replies: List['CommentResponse'] = []
    
    class Config:
        from_attributes = True

class ShareCreate(BaseModel):
    post_id: int

class FriendshipCreate(BaseModel):
    addressee_id: int

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    email: str
    password: str

class PostCreate(BaseModel):
    content: str
    post_type: str = "post"
    media_type: Optional[str] = None
    media_url: Optional[str] = None
    media_metadata: Optional[str] = None

class PostResponse(BaseModel):
    id: int
    author: Dict[str, Any]
    content: str
    post_type: str
    media_type: Optional[str] = None
    media_url: Optional[str] = None
    created_at: datetime
    reactions_count: int
    comments_count: int
    shares_count: int
    
    class Config:
        from_attributes = True

class StoryCreate(BaseModel):
    content: Optional[str] = None
    media_type: Optional[str] = None
    media_url: Optional[str] = None
    background_color: Optional[str] = None
    duration_hours: int = 24

class StoryResponse(BaseModel):
    id: int
    author: Dict[str, Any]
    content: Optional[str] = None
    media_type: Optional[str] = None
    media_url: Optional[str] = None
    background_color: Optional[str] = None
    created_at: datetime
    expires_at: datetime
    views_count: int
    
    class Config:
        from_attributes = True

class NotificationResponse(BaseModel):
    id: int
    notification_type: str
    title: str
    message: str
    data: Optional[str] = None
    is_read: bool
    created_at: datetime
    sender: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# Utility functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Get current user
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# WebSocket Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message)
                except:
                    self.active_connections[user_id].remove(connection)

    async def send_notification(self, user_id: int, notification: dict):
        message = json.dumps({
            "type": "notification",
            **notification
        })
        await self.send_personal_message(message, user_id)

manager = ConnectionManager()

def verify_websocket_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == email).first()
            return user
        finally:
            db.close()
    except JWTError:
        return None

# FastAPI app
app = FastAPI(title="Backend API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth routes
@app.post("/auth/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Verifica se o usuário já existe
        db_user = db.query(User).filter(User.email == user.email).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Cria novo usuário
        hashed_password = hash_password(user.password)
        
        # Converte birth_date string para objeto date
        birth_date_obj = user.get_birth_date_as_date() if user.birth_date else None
        
        db_user = User(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            password_hash=hashed_password,
            gender=user.gender,
            birth_date=birth_date_obj,
            phone=user.phone,
            is_active=True,
            created_at=datetime.utcnow(),
            last_seen=datetime.utcnow()
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    except Exception as e:
        print(f"Erro no registro: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@app.post("/auth/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == login_data.email).first()
        
        if not user or not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro no login: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno do servidor: {str(e)}")

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/auth/check-email")
def check_email_exists(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    return {"exists": user is not None}

@app.get("/auth/verify-token")
async def verify_token(current_user: User = Depends(get_current_user)):
    return {"valid": True, "user": current_user}

# Posts routes
@app.post("/posts/", response_model=PostResponse)
async def create_post(post: PostCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Validação e processamento do conteúdo
    content_to_save = post.content
    
    # Se for um depoimento, validamos se é JSON válido
    if post.post_type == "testimonial" and post.content:
        try:
            # Tenta fazer parse para validar se é JSON válido
            parsed_content = json.loads(post.content)
            
            # Verifica se tem a estrutura esperada
            if isinstance(parsed_content, dict) and 'content' in parsed_content and 'styles' in parsed_content:
                content_to_save = post.content
                print(f"✅ Depoimento JSON válido salvo: {parsed_content.get('content', '')[:50]}...")
            else:
                # Se não tem a estrutura esperada, trata como texto simples
                content_to_save = post.content
                print(f"⚠️ Estrutura JSON inválida, salvando como texto: {post.content[:50]}...")
        except (json.JSONDecodeError, TypeError) as e:
            # Se não for JSON válido, salva como texto simples
            content_to_save = post.content
            print(f"⚠️ JSON inválido, salvando como texto: {str(e)}")
    
    db_post = Post(
        author_id=current_user.id,
        content=content_to_save,
        post_type=post.post_type,
        media_type=post.media_type,
        media_url=post.media_url,
        media_metadata=post.media_metadata
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    return PostResponse(
        id=db_post.id,
        author={
            "id": db_post.author.id,
            "first_name": db_post.author.first_name,
            "last_name": db_post.author.last_name,
            "avatar": None
        },
        content=db_post.content,
        post_type=db_post.post_type,
        media_type=db_post.media_type,
        media_url=db_post.media_url,
        created_at=db_post.created_at,
        reactions_count=db_post.reactions_count,
        comments_count=db_post.comments_count,
        shares_count=db_post.shares_count
    )

@app.get("/posts/", response_model=List[PostResponse])
async def get_posts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    posts = db.query(Post).order_by(Post.created_at.desc()).limit(50).all()
    
    return [
        PostResponse(
            id=post.id,
            author={
                "id": post.author.id,
                "first_name": post.author.first_name,
                "last_name": post.author.last_name,
                "avatar": None
            },
            content=post.content,
            post_type=post.post_type,
            media_type=post.media_type,
            media_url=post.media_url,
            created_at=post.created_at,
            reactions_count=post.reactions_count,
            comments_count=post.comments_count,
            shares_count=post.shares_count
        )
        for post in posts
    ]

# User posts routes
@app.get("/users/{user_id}/posts", response_model=List[PostResponse])
async def get_user_posts(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    posts = db.query(Post).filter(
        Post.author_id == user_id,
        Post.post_type == "post"
    ).order_by(Post.created_at.desc()).limit(50).all()
    
    return [
        PostResponse(
            id=post.id,
            author={
                "id": post.author.id,
                "first_name": post.author.first_name,
                "last_name": post.author.last_name,
                "avatar": getattr(post.author, 'avatar', None)
            },
            content=post.content,
            post_type=post.post_type,
            media_type=post.media_type,
            media_url=post.media_url,
            created_at=post.created_at,
            reactions_count=db.query(Reaction).filter(Reaction.post_id == post.id).count(),
            comments_count=db.query(Comment).filter(Comment.post_id == post.id).count(),
            shares_count=db.query(Share).filter(Share.post_id == post.id).count()
        )
        for post in posts
    ]

@app.get("/users/{user_id}/testimonials", response_model=List[PostResponse])
async def get_user_testimonials(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    testimonials = db.query(Post).filter(
        Post.author_id == user_id,
        Post.post_type == "testimonial"
    ).order_by(Post.created_at.desc()).limit(50).all()
    
    return [
        PostResponse(
            id=post.id,
            author={
                "id": post.author.id,
                "first_name": post.author.first_name,
                "last_name": post.author.last_name,
                "avatar": getattr(post.author, 'avatar', None)
            },
            content=post.content,
            post_type=post.post_type,
            media_type=post.media_type,
            media_url=post.media_url,
            created_at=post.created_at,
            reactions_count=db.query(Reaction).filter(Reaction.post_id == post.id).count(),
            comments_count=db.query(Comment).filter(Comment.post_id == post.id).count(),
            shares_count=db.query(Share).filter(Share.post_id == post.id).count()
        )
        for post in testimonials
    ]

# Reactions routes
@app.post("/reactions/")
async def create_reaction(reaction: ReactionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if post exists
    post = db.query(Post).filter(Post.id == reaction.post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Valid reaction types
    valid_reactions = ["like", "love", "haha", "wow", "sad", "angry"]
    if reaction.reaction_type not in valid_reactions:
        raise HTTPException(status_code=400, detail="Invalid reaction type")
    
    # Check if user already reacted to this post
    existing_reaction = db.query(Reaction).filter(
        Reaction.user_id == current_user.id,
        Reaction.post_id == reaction.post_id
    ).first()
    
    if existing_reaction:
        if existing_reaction.reaction_type == reaction.reaction_type:
            # Remove reaction if same type
            db.delete(existing_reaction)
            db.commit()
            return {"message": "Reaction removed"}
        else:
            # Update reaction type
            existing_reaction.reaction_type = reaction.reaction_type
            db.commit()
            return {"message": "Reaction updated"}
    
    # Create new reaction
    db_reaction = Reaction(
        user_id=current_user.id,
        post_id=reaction.post_id,
        reaction_type=reaction.reaction_type
    )
    db.add(db_reaction)
    db.commit()
    
    # Send notification to post author if not self-reaction
    if post.author_id != current_user.id:
        notification = Notification(
            recipient_id=post.author_id,
            sender_id=current_user.id,
            notification_type="reaction",
            title=f"{current_user.first_name} {current_user.last_name}",
            message=f"reagiu ao seu post com {reaction.reaction_type}",
            data=json.dumps({"post_id": reaction.post_id}),
            created_at=datetime.utcnow()
        )
        db.add(notification)
        db.commit()
        
        # Send real-time notification
        await manager.send_notification(post.author_id, {
            "id": notification.id,
            "type": "reaction",
            "title": f"{current_user.first_name} {current_user.last_name}",
            "message": f"reagiu ao seu post com {reaction.reaction_type}",
            "sender": {
                "id": current_user.id,
                "first_name": current_user.first_name,
                "last_name": current_user.last_name,
                "avatar": getattr(current_user, 'avatar', None)
            },
            "data": {"post_id": reaction.post_id},
            "created_at": notification.created_at.isoformat()
        })
    
    return {"message": "Reaction created"}

@app.get("/reactions/post/{post_id}")
async def get_post_reactions(post_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    reactions = db.query(Reaction).filter(Reaction.post_id == post_id).all()
    
    # Group reactions by type
    reaction_counts = {}
    user_reaction = None
    
    for reaction in reactions:
        if reaction.reaction_type not in reaction_counts:
            reaction_counts[reaction.reaction_type] = 0
        reaction_counts[reaction.reaction_type] += 1
        
        if reaction.user_id == current_user.id:
            user_reaction = reaction.reaction_type
    
    return {
        "reactions": reaction_counts,
        "user_reaction": user_reaction,
        "total": len(reactions)
    }

# Comments routes
@app.post("/comments/", response_model=CommentResponse)
async def create_comment(comment: CommentCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
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
    
    # Send notification to post author
    if post.author_id != current_user.id:
        notification = Notification(
            recipient_id=post.author_id,
            sender_id=current_user.id,
            notification_type="comment",
            title=f"{current_user.first_name} {current_user.last_name}",
            message="comentou no seu post",
            data=json.dumps({"post_id": comment.post_id, "comment_id": db_comment.id}),
            created_at=datetime.utcnow()
        )
        db.add(notification)
        db.commit()
        
        # Send real-time notification
        await manager.send_notification(post.author_id, {
            "id": notification.id,
            "type": "comment",
            "title": f"{current_user.first_name} {current_user.last_name}",
            "message": "comentou no seu post",
            "sender": {
                "id": current_user.id,
                "first_name": current_user.first_name,
                "last_name": current_user.last_name,
                "avatar": getattr(current_user, 'avatar', None)
            },
            "data": {"post_id": comment.post_id, "comment_id": db_comment.id},
            "created_at": notification.created_at.isoformat()
        })
    
    return CommentResponse(
        id=db_comment.id,
        content=db_comment.content,
        author={
            "id": db_comment.author.id,
            "first_name": db_comment.author.first_name,
            "last_name": db_comment.author.last_name,
            "avatar": getattr(db_comment.author, 'avatar', None)
        },
        created_at=db_comment.created_at,
        reactions_count=0,
        replies=[]
    )

@app.get("/comments/post/{post_id}", response_model=List[CommentResponse])
async def get_post_comments(post_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.post_id == post_id, Comment.parent_id.is_(None)).all()
    
    result = []
    for comment in comments:
        replies = db.query(Comment).filter(Comment.parent_id == comment.id).all()
        result.append(CommentResponse(
            id=comment.id,
            content=comment.content,
            author={
                "id": comment.author.id,
                "first_name": comment.author.first_name,
                "last_name": comment.author.last_name,
                "avatar": getattr(comment.author, 'avatar', None)
            },
            created_at=comment.created_at,
            reactions_count=0,
            replies=[
                CommentResponse(
                    id=reply.id,
                    content=reply.content,
                    author={
                        "id": reply.author.id,
                        "first_name": reply.author.first_name,
                        "last_name": reply.author.last_name,
                        "avatar": getattr(reply.author, 'avatar', None)
                    },
                    created_at=reply.created_at,
                    reactions_count=0,
                    replies=[]
                ) for reply in replies
            ]
        ))
    
    return result

# Shares routes
@app.post("/shares/")
async def share_post(share: ShareCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
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

# Friendships routes
@app.post("/friendships/")
async def send_friend_request(friendship: FriendshipCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if user exists
    addressee = db.query(User).filter(User.id == friendship.addressee_id, User.is_active == True).first()
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
        if existing_friendship.status == "pending":
            raise HTTPException(status_code=400, detail="Friend request already sent")
        elif existing_friendship.status == "accepted":
            raise HTTPException(status_code=400, detail="Already friends")
    
    # Create friendship request
    db_friendship = Friendship(
        requester_id=current_user.id,
        addressee_id=friendship.addressee_id,
        status="pending"
    )
    db.add(db_friendship)
    db.commit()
    
    # Send notification
    notification = Notification(
        recipient_id=friendship.addressee_id,
        sender_id=current_user.id,
        notification_type="friend_request",
        title=f"{current_user.first_name} {current_user.last_name}",
        message="enviou uma solicitação de amizade",
        data=json.dumps({"friendship_id": db_friendship.id}),
        created_at=datetime.utcnow()
    )
    db.add(notification)
    db.commit()
    
    # Send real-time notification
    await manager.send_notification(friendship.addressee_id, {
        "id": notification.id,
        "type": "friend_request",
        "title": f"{current_user.first_name} {current_user.last_name}",
        "message": "enviou uma solicitação de amizade",
        "sender": {
            "id": current_user.id,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "avatar": getattr(current_user, 'avatar', None)
        },
        "data": {"friendship_id": db_friendship.id},
        "created_at": notification.created_at.isoformat()
    })
    
    return {"message": "Friend request sent successfully"}

@app.put("/friendships/{friendship_id}/accept")
async def accept_friend_request(friendship_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    friendship = db.query(Friendship).filter(Friendship.id == friendship_id).first()
    if not friendship:
        raise HTTPException(status_code=404, detail="Friend request not found")
    
    if friendship.addressee_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to accept this request")
    
    if friendship.status != "pending":
        raise HTTPException(status_code=400, detail="Friend request is not pending")
    
    friendship.status = "accepted"
    friendship.updated_at = datetime.utcnow()
    db.commit()
    
    # Send notification to requester
    notification = Notification(
        recipient_id=friendship.requester_id,
        sender_id=current_user.id,
        notification_type="friend_accept",
        title=f"{current_user.first_name} {current_user.last_name}",
        message="aceitou sua solicitação de amizade",
        data=json.dumps({"friendship_id": friendship_id}),
        created_at=datetime.utcnow()
    )
    db.add(notification)
    db.commit()
    
    # Send real-time notification
    await manager.send_notification(friendship.requester_id, {
        "id": notification.id,
        "type": "friend_accept",
        "title": f"{current_user.first_name} {current_user.last_name}",
        "message": "aceitou sua solicitação de amizade",
        "sender": {
            "id": current_user.id,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "avatar": getattr(current_user, 'avatar', None)
        },
        "data": {"friendship_id": friendship_id},
        "created_at": notification.created_at.isoformat()
    })
    
    return {"message": "Friend request accepted"}

@app.put("/friendships/{friendship_id}/reject")
async def reject_friend_request(friendship_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    friendship = db.query(Friendship).filter(Friendship.id == friendship_id).first()
    if not friendship:
        raise HTTPException(status_code=404, detail="Friend request not found")
    
    if friendship.addressee_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to reject this request")
    
    if friendship.status != "pending":
        raise HTTPException(status_code=400, detail="Friend request is not pending")
    
    friendship.status = "rejected"
    friendship.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Friend request rejected"}

@app.get("/friendships/status/{user_id}")
async def get_friendship_status(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    friendship = db.query(Friendship).filter(
        ((Friendship.requester_id == current_user.id) & (Friendship.addressee_id == user_id)) |
        ((Friendship.requester_id == user_id) & (Friendship.addressee_id == current_user.id))
    ).first()
    
    if not friendship:
        return {"status": "none"}
    
    return {"status": friendship.status}

# User search
@app.get("/users/")
async def search_users(search: str = "", current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not search.strip():
        return []
    
    users = db.query(User).filter(
        User.is_active == True,
        User.id != current_user.id,
        (User.first_name.ilike(f"%{search}%") | User.last_name.ilike(f"%{search}%") | User.email.ilike(f"%{search}%"))
    ).limit(20).all()
    
    return [
        {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "avatar": getattr(user, 'avatar', None)
        }
        for user in users
    ]

# Get user by ID
@app.get("/users/{user_id}")
async def get_user_by_id(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "bio": getattr(user, 'bio', None),
        "avatar": getattr(user, 'avatar', None),
        "birth_date": user.birth_date.isoformat() if user.birth_date else None,
        "created_at": user.created_at.isoformat()
    }

# Mark all notifications as read
@app.put("/notifications/mark-all-read")
async def mark_all_notifications_as_read(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(Notification).filter(
        Notification.recipient_id == current_user.id,
        Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    
    return {"message": "All notifications marked as read"}

# Delete notification
@app.delete("/notifications/{notification_id}")
async def delete_notification(notification_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.recipient_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    db.delete(notification)
    db.commit()
    
    return {"message": "Notification deleted"}

# Delete post
@app.delete("/posts/{post_id}")
async def delete_post(post_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    
    # Delete related data
    db.query(Reaction).filter(Reaction.post_id == post_id).delete()
    db.query(Comment).filter(Comment.post_id == post_id).delete()
    db.query(Share).filter(Share.post_id == post_id).delete()
    
    db.delete(post)
    db.commit()
    
    return {"message": "Post deleted successfully"}

# Stories routes
@app.post("/stories/", response_model=StoryResponse)
async def create_story(story: StoryCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    expires_at = datetime.utcnow() + timedelta(hours=story.duration_hours)
    
    db_story = Story(
        author_id=current_user.id,
        content=story.content,
        media_type=story.media_type,
        media_url=story.media_url,
        background_color=story.background_color,
        duration_hours=story.duration_hours,
        expires_at=expires_at
    )
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    
    return StoryResponse(
        id=db_story.id,
        author={
            "id": db_story.author.id,
            "first_name": db_story.author.first_name,
            "last_name": db_story.author.last_name,
            "avatar": None
        },
        content=db_story.content,
        media_type=db_story.media_type,
        media_url=db_story.media_url,
        background_color=db_story.background_color,
        created_at=db_story.created_at,
        expires_at=db_story.expires_at,
        views_count=0
    )

@app.get("/stories/", response_model=List[StoryResponse])
async def get_stories(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Get stories that haven't expired
    now = datetime.utcnow()
    stories = db.query(Story).filter(Story.expires_at > now).order_by(Story.created_at.desc()).all()
    
    return [
        StoryResponse(
            id=story.id,
            author={
                "id": story.author.id,
                "first_name": story.author.first_name,
                "last_name": story.author.last_name,
                "avatar": None
            },
            content=story.content,
            media_type=story.media_type,
            media_url=story.media_url,
            background_color=story.background_color,
            created_at=story.created_at,
            expires_at=story.expires_at,
            views_count=db.query(StoryView).filter(StoryView.story_id == story.id).count()
        )
        for story in stories
    ]

@app.post("/stories/{story_id}/view")
async def view_story(story_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
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

@app.delete("/stories/{story_id}")
async def delete_story(story_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    if story.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this story")
    
    # Delete story views first
    db.query(StoryView).filter(StoryView.story_id == story_id).delete()
    
    # Delete the story
    db.delete(story)
    db.commit()
    
    return {"message": "Story deleted successfully"}

# Notifications routes
@app.get("/notifications/", response_model=List[NotificationResponse])
async def get_notifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notifications = db.query(Notification).filter(
        Notification.recipient_id == current_user.id
    ).order_by(Notification.created_at.desc()).limit(50).all()
    
    return [
        NotificationResponse(
            id=notification.id,
            notification_type=notification.notification_type,
            title=notification.title,
            message=notification.message,
            data=notification.data,
            is_read=notification.is_read,
            created_at=notification.created_at,
            sender={
                "id": notification.sender.id,
                "name": f"{notification.sender.first_name} {notification.sender.last_name}"
            } if notification.sender else None
        )
        for notification in notifications
    ]

@app.get("/notifications/unread-count")
async def get_unread_notifications_count(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    count = db.query(Notification).filter(
        Notification.recipient_id == current_user.id,
        Notification.is_read == False
    ).count()
    
    return {"count": count}

@app.put("/notifications/{notification_id}/read")
async def mark_notification_as_read(notification_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.recipient_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = True
    db.commit()
    
    return {"message": "Notification marked as read"}

# Friendships routes
@app.get("/friendships/pending-count")
async def get_pending_friendships_count(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    count = db.query(Friendship).filter(
        Friendship.addressee_id == current_user.id,
        Friendship.status == "pending"
    ).count()
    
    return {"count": count}

@app.get("/friendships/pending")
async def get_pending_friendships(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    friendships = db.query(Friendship).filter(
        Friendship.addressee_id == current_user.id,
        Friendship.status == "pending"
    ).all()
    
    return [
        {
            "id": friendship.id,
            "requester": {
                "id": friendship.requester.id,
                "first_name": friendship.requester.first_name,
                "last_name": friendship.requester.last_name,
                "avatar": None
            },
            "created_at": friendship.created_at
        }
        for friendship in friendships
    ]

# WebSocket endpoint
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    # Get token from query parameters
    query_params = dict(websocket.query_params)
    token = query_params.get('token')
    
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # Verify token
    user = verify_websocket_token(token)
    if not user or user.id != user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo message back for testing
            await manager.send_personal_message(f"Echo: {data}", user_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)

# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Create tables
Base.metadata.create_all(bind=engine)

# Função para inicializar o banco com dados de exemplo
def init_sample_data():
    db = SessionLocal()
    try:
        # Verifica se já existem usuários
        if db.query(User).count() == 0:
            # Cria usuário de exemplo
            sample_user = User(
                first_name="João",
                last_name="Silva",
                email="joao@exemplo.com",
                password_hash=hash_password("123456"),
                gender="M",
                is_active=True,
                created_at=datetime.utcnow(),
                last_seen=datetime.utcnow()
            )
            db.add(sample_user)
            db.commit()
            db.refresh(sample_user)
            
            # Cria post de exemplo
            sample_post = Post(
                author_id=sample_user.id,
                content="Bem-vindos à nossa rede social! 🎉",
                post_type="post",
                created_at=datetime.utcnow()
            )
            db.add(sample_post)
            db.commit()
            
            print("✅ Dados de exemplo criados com sucesso!")
            print(f"📧 Email: {sample_user.email}")
            print("🔑 Senha: 123456")
    except Exception as e:
        print(f"❌ Erro ao criar dados de exemplo: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Inicializa dados de exemplo na primeira execução
    init_sample_data()
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)