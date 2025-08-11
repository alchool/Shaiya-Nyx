from sqlalchemy.orm import Session
from . import models, auth
from app.models import User

# Registrazione account
def create_user(db: Session, username: str, password: str, email: str | None = None):
    hashed = auth.get_password_hash(password)
    user = models.UserMaster(UserID=username, Pw=hashed, Email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Login
def authenticate_user(db: Session, username: str, password: str):
    user = auth.get_user_by_username(db, username)
    if not user:
        return None
    if not auth.verify_password(password, user.Pw):
        return None
    return user

# Leaderboard
def get_top_pvp(db: Session, limit: int = 50):
    # ordina per somma K1..K4
    return db.query(models.Char).order_by((models.Char.K1+models.Char.K2+models.Char.K3+models.Char.K4).desc()).limit(limit).all()

# Inventory
def get_inventory_for_char(db: Session, char_id: int):
    return db.query(models.Inventory).filter(models.Inventory.CharID == char_id).all()

#ottini utente
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()
