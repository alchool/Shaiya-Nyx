import os
from sqlalchemy.orm import Session
from .db import SessionLocal
from .models import UserMaster

# ATTENZIONE: esempi semplificati. Validare sempre le transazioni con le API del provider.

def handle_stripe_webhook(payload: bytes, sig_header: str):
    # verificare con stripe.WebhookSignature
    # se pagamento confermato: aggiornare UserMaster.Point
    return { 'status': 'ok' }

async def handle_paypal_ipn(formdata):
    # verificare tramite POST a PayPal (verify) e controllare payment_status
    # esempio: update utenti
    return { 'status': 'ok' }

# helper per aggiornare punti
def credit_user_points(user_id: str, amount: int):
    db: Session = SessionLocal()
    try:
        user = db.query(UserMaster).filter(UserMaster.UserID == user_id).first()
        if not user:
            return False
        user.Point = (user.Point or 0) + amount
        db.commit()
        return True
    finally:
        db.close()
