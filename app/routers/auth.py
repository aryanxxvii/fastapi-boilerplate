import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from ..schemas import UserCreate
from ..database import get_db
from ..models import User
from ..config import SECRET_KEY
import datetime
from datetime import timedelta

auth_router = APIRouter()
oauth_scheme = OAuth2PasswordBearer(tokenUrl="login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_token(username: str, expires: int = 30):
    expiry_date = datetime.datetime.now(datetime.timezone.utc) + timedelta(minutes=expires)

    payload = {"sub": username, "exp": expiry_date}
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def get_current_user(token: str = Depends(oauth_scheme), db = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user.username


@auth_router.post("/register")
def register(user_data: UserCreate, db = Depends(get_db)):
    hashed_password = pwd_context.hash(user_data.password)
    user = User(username=user_data.username, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {'User successfully registered'}

@auth_router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)):
    username = form_data.username
    password = form_data.password

    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials")
    
    if not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials")
    
    token = create_token(username)

    return {"access_token": token, "token_type": "bearer"}






