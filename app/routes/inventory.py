from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..deps import get_db
from ..crud import get_inventory_for_char

router = APIRouter(prefix='/inventory', tags=['inventory'])

@router.get('/{char_id}')
def inventory(char_id: int, db: Session = Depends(get_db)):
    inv = get_inventory_for_char(db, char_id)
    return [ { 'ItemID': i.ItemID, 'Count': i.Count } for i in inv ]
