# app/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Form
from app.security import create_access_token
from app.dependencies import get_current_user
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter()

@router.post("/token")
def login_for_access_token(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    # Controlla credenziali (esempio, da adattare)
    user = db.execute("SELECT UserID, Pw FROM PS_UserData.dbo.Users_Master WHERE UserID=:username", {"username": username}).fetchone()
    if not user or user.Pw != password:
        raise HTTPException(status_code=401, detail="Credenziali errate")
    
    access_token = create_access_token(data={"sub": username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
def read_users_me(current_user: str = Depends(get_current_user)):
    return {"username": current_user}
