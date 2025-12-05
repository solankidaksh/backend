from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import UserCreate, UserLogin, UserResponse
from auth.hashing import hash_password, verify_password
from auth.jwt_handler import create_access_token, verify_token

router = APIRouter(prefix="/auth", tags=["Auth"])

# --------------------------
# SIGNUP
# --------------------------
@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# --------------------------
# LOGIN
# --------------------------
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"user_id": db_user.id})
    return {"access_token": token, "token_type": "bearer"}


# --------------------------
# GET CURRENT USER
# --------------------------
def get_current_user(db: Session = Depends(get_db), token: str = Depends(lambda req: req.headers.get("Authorization"))):

    if not token:
        raise HTTPException(status_code=401, detail="Token missing")

    token = token.replace("Bearer ", "")
    payload = verify_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == payload["user_id"]).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
