# Shaiya-Nyx
struttura di progetto completa (back-end in Python) per integrare un sito web con il database di Shaiya Essentials (MS SQL), includendo: registrazione account, login/profilo, classifiche PvP/EXP, visualizzazione inventario/PG, shop/donazioni (AP), e sistema ticket.

# ALBERO DEL PROGETTO

```
shaiya-web-python/
├── README.md
├── requirements.txt
├── .env.example
├── alembic/                 # (placeholder) migrazioni DB
├── Dockerfile               # opzionale
├── start.bat                # script per avviare su Windows (es. uvicorn)
├── main.py
├── app/
│   ├── __init__.py
│   ├── db.py                # connessione a MS SQL + session
│   ├── models.py            # SQLAlchemy models (mappati alle tabelle Shaiya)
│   ├── schemas.py           # Pydantic schemas
│   ├── crud.py              # funzioni DB riutilizzabili
│   ├── auth.py              # autenticazione, JWT, hashing password
│   ├── payments.py          # webhook per PayPal/Stripe + logica AP
│   ├── deps.py              # dipendenze FastAPI (get_db, current_user)
│   └── routes/
│       ├── accounts.py      # registrazione, login, reset password, profilo
│       ├── leaderboard.py   # endpoints PvP/EXP
│       ├── inventory.py     # visualizzazione inventario/pg
│       ├── shop.py          # acquisto AP, checkout init
│       └── tickets.py       # CRUD ticket & support
├── templates/               # Jinja2 templates (opzionali)
│   ├── base.html
│   ├── register.html
│   └── profile.html
└── static/
    └── css/
    # ISTRUZIONI RAPIDE

1. Copiare `.env.example` -> `.env` e inserire la stringa di connessione a MS SQL (vedi sez. README).
2. Creare un virtualenv (Windows): `python -m venv .venv` e attivarlo.
3. Installare dipendenze: `pip install -r requirements.txt`.
4. Avviare: `uvicorn main:app --reload --host 0.0.0.0 --port 8000` (oppure usare `start.bat`).

# NOTE DI SICUREZZA E INTEGRAZIONE

- **Password:** se il database Shaiya originale memorizza password con un algoritmo diverso dal bcrypt, dovrete adattare la registrazione per creare password compatibili col server di gioco (oppure creare un processo che sincronizzi password con l'hash richiesto). Verificare la gestione `Pw` nella tabella `Users_Master` del vostro DB.
- **Connessione al DB di gioco:** lavorare sempre su copia del DB per sviluppo. Evitare operazioni destructive in produzione.
- **Webhooks di pagamento:** usare la verifica ufficiale dei provider (Stripe signature, PayPal IPN verify) prima di applicare AP.
- **SQL injection:** usare sempre query parametrizzate (SQLAlchemy ORM + session) e non costruire stringhe SQL concatenate.
- **HTTPS & CORS:** servire il sito via HTTPS e configurare CORS correttamente.

