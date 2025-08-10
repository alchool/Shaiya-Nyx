# database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Carica variabili da .env
load_dotenv()

DB_URL = os.getenv(
    "DB_URL",
    "mssql+pyodbc://user:password@localhost/PS_UserData?driver=ODBC+Driver+17+for+SQL+Server"
)

# Engine SQLAlchemy
engine = create_engine(DB_URL, echo=False, future=True)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base per i modelli ORM
Base = declarative_base()

# Dependency FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Configurazione della connessione al database
DATABASE_URL = os.getenv("DATABASE_URL", "mssql+pyodbc://username:password@localhost/PS_GameData?driver=ODBC+Driver+17+for+SQL+Server")

# Creazione dell'engine e della sessione
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base per i modelli
Base = declarative_base()
