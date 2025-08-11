# app/logging.py
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("shaiya")
logger.setLevel(logging.INFO)

handler = RotatingFileHandler("logs/app.log", maxBytes=10*1024*1024, backupCount=5)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# Integrazione con uvicorn access log
import uvicorn
uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.handlers.append(handler)
