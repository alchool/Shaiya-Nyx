from fastapi import APIRouter, Request, Header
from ..payments import handle_stripe_webhook, handle_paypal_ipn

router = APIRouter(prefix='/shop', tags=['shop'])

@router.post('/stripe/webhook')
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get('stripe-signature')
    return await handle_stripe_webhook(payload, sig)

@router.post('/paypal/ipn')
async def paypal_ipn(request: Request):
    form = await request.form()
    return await handle_paypal_ipn(form)
