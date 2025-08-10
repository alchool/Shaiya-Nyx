from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, crud
from ..deps import get_db
from ..auth import create_access_token

router = APIRouter(prefix="/accounts", tags=["accounts"])

@router.post('/register', response_model=schemas.UserOut)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = crud.get_user_by_username(db, payload.username)
    if existing:
        raise HTTPException(status_code=400, detail='Username already exists')
    user = crud.create_user(db, payload.username, payload.password, payload.email)
    return user

@router.post('/login', response_model=schemas.Token)
def login(form_data: schemas.UserCreate, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail='Invalid credentials')
    token = create_access_token({"sub": user.UserID})
    return {"access_token": token, "token_type": "bearer"}
