# app/payments.py
import os
import json
import requests
from decimal import Decimal
from fastapi import APIRouter, Request, Depends, HTTPException, status
from .deps import get_db, get_current_user
from .models import DonationLog, User

router = APIRouter()

PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_SECRET = os.getenv("PAYPAL_SECRET")
PAYPAL_API = os.getenv("PAYPAL_API_URL", "https://api-m.sandbox.paypal.com")
AP_RATE = int(os.getenv("AP_RATE", "100"))  # 1 USD = 100 AP

@router.post("/donate/create")
def create_donation(
    current_user=Depends(get_current_user),
    amount_usd: float = 5.0,
    db=Depends(get_db)
):
    """
    Crea un ordine PayPal e restituisce il link per approvazione.
    Collega la transazione all'utente con custom_id.
    """
    # Access Token
    resp = requests.post(
        f"{PAYPAL_API}/v1/oauth2/token",
        headers={"Accept": "application/json"},
        data={"grant_type": "client_credentials"},
        auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET)
    )
    resp.raise_for_status()
    token = resp.json()["access_token"]

    # Creazione ordine con custom_id per legare la transazione all'utente
    order = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {"currency_code": "USD", "value": f"{amount_usd:.2f}"},
            "custom_id": str(current_user.UserUID)
        }],
        "application_context": {
            "return_url": os.getenv("PAYPAL_RETURN_URL"),
            "cancel_url": os.getenv("PAYPAL_CANCEL_URL")
        }
    }

    resp = requests.post(
        f"{PAYPAL_API}/v2/checkout/orders",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        },
        data=json.dumps(order)
    )
    resp.raise_for_status()
    data = resp.json()

    # Trova URL approvazione
    for link in data.get("links", []):
        if link["rel"] == "approve":
            return {"redirect_url": link["href"]}

    raise HTTPException(status_code=400, detail="Order creation failed")


@router.post("/donate/webhook")
async def paypal_webhook(request: Request, db=Depends(get_db)):
    """
    Webhook PayPal - accredita AP dopo verifica firma.
    """
    event = await request.json()

    # TODO: Verifica firma webhook PayPal (importante per la sicurezza!)
    # Guida: https://developer.paypal.com/docs/api/webhooks/v1/#verify-webhook-signature_post

    if event.get("event_type") == "CHECKOUT.ORDER.APPROVED":
        try:
            txn_id = event["resource"]["id"]
            amount_usd = float(event["resource"]["purchase_units"][0]["amount"]["value"])
            ap_amount = int(amount_usd * AP_RATE)
            custom_id = event["resource"]["purchase_units"][0].get("custom_id")

            # Recupero utente da custom_id
            user = db.query(User).filter_by(UserUID=int(custom_id)).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Aggiorno AP
            user.Point = (user.Point or 0) + ap_amount

            # Log transazione
            db.add(DonationLog(
                UserUID=user.UserUID,
                UserID=user.UserID,
                AmountUSD=Decimal(amount_usd),
                APGranted=ap_amount,
                PayPalTxnID=txn_id,
                Status="APPROVED"
            ))

            db.commit()
            db.refresh(user)

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return {"status": "ok"}

