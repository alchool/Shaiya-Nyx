from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..deps import get_db
from ..crud import get_top_pvp
from ..schemas import CharOut

router = APIRouter(prefix='/leaderboard', tags=['leaderboard'])

@router.get('/pvp', response_model=list[CharOut])
def pvp_list(limit: int = 50, db: Session = Depends(get_db)):
    chars = get_top_pvp(db, limit)
    # trasformare in CharOut con kills totali
    out = []
    for c in chars:
        kills = (c.K1 or 0) + (c.K2 or 0) + (c.K3 or 0) + (c.K4 or 0)
        out.append( CharOut.from_orm(c).dict() | { 'kills': kills } )
    return out
