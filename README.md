# Shaiya-Nyx
struttura di progetto completa (back-end in Python) per integrare un sito web con il database di Shaiya Essentials (MS SQL), includendo: registrazione account, login/profilo, classifiche PvP/EXP, visualizzazione inventario/PG, shop/donazioni (AP), e sistema ticket.

Dipendenze principali
main.py (file principale) dipende da:
app/routes/auth.py e user.py (importati come router)
app/config.py (per le impostazioni)
app/payments.py (router pagamenti)
app/db.py (per SessionLocal)
models.py (per DonationLog e User)
templates/*.html (per il rendering delle pagine)
app/config.py gestisce:
Variabili d'ambiente dal file .env
Configurazioni globali usate in altri moduli
app/db.py e database.py gestiscono:
Connessione database
Sessioni SQLAlchemy
Usati da quasi tutti i moduli che necessitano accesso DB
app/routes/ contiene i router che dipendono da:
app/models.py (definizioni modelli DB)
app/schemas.py (Pydantic models)
app/deps.py (dipendenze comuni)
app/crud.py (operazioni DB)
templates/ dipende da:
base.html (template base ereditato dagli altri)
File statici (CSS/JS)
Frontend/ dipende da:
app.js (logica frontend)
style.css (stili)
API esposte dal backend

# ALBERO DEL PROGETTO
Backend in Python: Utilizza FastAPI per la gestione delle rotte e SQLAlchemy per l'interazione con il database.

Gestione delle migrazioni del database: È presente una cartella alembic/, che funge da placeholder per le migrazioni del database.

Configurazione ambientale: Un file .env.example per la configurazione delle variabili d'ambiente.

Script di avvio: Un file start.bat per avviare il server su Windows.

File di dipendenze: Un file requirements.txt che elenca le librerie necessarie.

Template HTML: Una cartella templates/ per i template Jinja2.

Moduli applicativi: Una cartella app/ che contiene i moduli principali dell'applicazione, inclusi main.py per la configurazione di FastAPI, models.py per i modelli del database e database.py per la gestione della connessione al database.
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

