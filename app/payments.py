# Import necessari
import os, json, requests
from fastapi import APIRouter, Request, Depends, HTTPException
from .deps import get_db, get_current_user  # dipendenze esistenti
from .models import DonationLog, User  # SQLAlchemy modeli
from decimal import Decimal

router = APIRouter()

PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_SECRET = os.getenv("PAYPAL_SECRET")
PAYPAL_API = os.getenv("PAYPAL_API_URL", "https://api-m.sandbox.paypal.com")
AP_RATE = int(os.getenv("AP_RATE", "100"))  # 1 USD → 100 AP

@router.post("/donate/create")
def create_donation(current_user=Depends(get_current_user), amount_usd: float = 5.0, db=Depends(get_db)):
    # Ottieni access token
    resp = requests.post(
        f"{PAYPAL_API}/v1/oauth2/token",
        headers={"Accept": "application/json"},
        data={"grant_type": "client_credentials"},
        auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET)
    )
    resp.raise_for_status()
    token = resp.json()["access_token"]

    # Costruisci ordine
    order = {
        "intent": "CAPTURE",
        "purchase_units": [{"amount": {"currency_code": "USD", "value": f"{amount_usd:.2f}"}}],
        "application_context": {
            "return_url": os.getenv("PAYPAL_RETURN_URL"),
            "cancel_url": os.getenv("PAYPAL_CANCEL_URL")
        }
    }

    resp = requests.post(f"{PAYPAL_API}/v2/checkout/orders",
                         headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
                         data=json.dumps(order))
    resp.raise_for_status()
    data = resp.json()
    for link in data.get("links", []):
        if link["rel"] == "approve":
            return {"redirect_url": link["href"]}
    raise HTTPException(status_code=400, detail="Order creation failed")

@router.post("/donate/webhook")
async def paypal_webhook(request: Request, db=Depends(get_db)):
    event = await request.json()
    # Qui verificare la firma/validità del webhook secondo PayPal
    if event.get("event_type") == "CHECKOUT.ORDER.APPROVED":
        txn_id = event["resource"]["id"]
        amount_usd = float(event["resource"]["purchase_units"][0]["amount"]["value"])
        ap_amount = int(amount_usd * AP_RATE)
        payer_email = event["resource"]["payer"]["email_address"]

        user = db.query(User).filter_by(email=payer_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.Point += ap_amount  # aggiorna AP
        db.add(DonationLog(
            UserUID=user.UserUID,
            UserID=user.UserID,
            AmountUSD=Decimal(amount_usd),
            APGranted=ap_amount,
            PayPalTxnID=txn_id,
            Status="APPROVED"
        ))
        db.commit()
    return {"status": "ok"}
