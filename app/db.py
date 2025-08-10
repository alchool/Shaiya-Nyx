```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv('MSSQL_HOST', '127.0.0.1')
PORT = os.getenv('MSSQL_PORT', '1433')
DB = os.getenv('MSSQL_DB', 'ShaiyaDB')
USER = os.getenv('MSSQL_USER', 'sa')
PASS = os.getenv('MSSQL_PASS', '')

# Connessione ODBC per SQL Server
params = quote_plus(f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={HOST},{PORT};DATABASE={DB};UID={USER};PWD={PASS}")
SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={params}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# Base per i modeli
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
```
