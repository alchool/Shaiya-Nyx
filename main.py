from fastapi import FastAPI
from app.routes import accounts, leaderboard, inventory, shop, tickets
from app.db import Base, engine

# Creare le tabelle ORM (opzionale: usare Alembic nelle migrazioni)
Base.metadata.create_all(bind=engine)

app = FastAPI(title='Shaiya Web - API')
app.include_router(accounts.router)
app.include_router(leaderboard.router)
app.include_router(inventory.router)
app.include_router(shop.router)
app.include_router(tickets.router)

@app.get('/')
def root():
    return { 'ok': True }
