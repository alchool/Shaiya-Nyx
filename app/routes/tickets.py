from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..deps import get_db

router = APIRouter(prefix='/tickets', tags=['tickets'])

# Semplice sistema ticket
TICKETS = []  # per produzione usare DB

@router.post('/create')
def create_ticket(subject: str, body: str, user: str):
    t = { 'id': len(TICKETS)+1, 'subject': subject, 'body': body, 'user': user, 'status': 'open' }
    TICKETS.append(t)
    return t

@router.get('/{ticket_id}')
def get_ticket(ticket_id: int):
    for t in TICKETS:
        if t['id'] == ticket_id:
            return t
    raise HTTPException(status_code=404, detail='Ticket not found')
