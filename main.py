from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pyodbc
import os

app = FastAPI()

# Monta cartella static
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Connessione a SQL Server Shaiya Essentials
def get_db_connection():
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={os.getenv('DB_HOST','localhost')};"
        f"DATABASE={os.getenv('DB_NAME','PS_GameData')};"
        f"UID={os.getenv('DB_USER','sa')};"
        f"PWD={os.getenv('DB_PASSWORD','password')}"
    )
    return conn

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register", response_class=HTMLResponse, name="register_post")
def register_post(request: Request, username: str = Form(...), password: str = Form(...), email: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO PS_UserData.dbo.Users_Master (UserID, Pw, Email) VALUES (?, ?, ?)",
        (username, password, email)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return templates.TemplateResponse("register.html", {"request": request, "message": "Account creato con successo"})

@app.get("/profile", response_class=HTMLResponse)
def profile(request: Request):
    # esempio: user statico
    user = {"username": "TestUser", "email": "test@example.com", "kills": 150, "exp": 30000, "ap": 500}
    inventory = [{"slot": 1, "name": "Spada Epica", "quantity": 1}]
    return templates.TemplateResponse("profile.html", {"request": request, "user": user, "inventory": inventory})

@app.get("/pvp_rankings", response_class=HTMLResponse)
def pvp_rankings(request: Request):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT TOP 50 CharName, K1, Level FROM PS_GameData.dbo.Chars ORDER BY K1 DESC")
    rankings = [{"name": row.CharName, "kills": row.K1, "level": row.Level} for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return templates.TemplateResponse("pvp_rankings.html", {"request": request, "rankings": rankings})

@app.get("/inventory", response_class=HTMLResponse)
def inventory(request: Request):
    inventory = [{"slot": 1, "name": "Pozione HP", "quantity": 10}]
    return templates.TemplateResponse("inventory.html", {"request": request, "inventory": inventory})

@app.get("/shop", response_class=HTMLResponse)
def shop(request: Request):
    shop_items = [
        {"id": 1, "name": "Cassa Premium", "description": "Contiene oggetti rari", "price": 100},
        {"id": 2, "name": "Set Armatura", "description": "Armatura completa epica", "price": 500}
    ]
    return templates.TemplateResponse("shop.html", {"request": request, "shop_items": shop_items})

@app.post("/buy_item", response_class=HTMLResponse, name="buy_item")
def buy_item(request: Request, item_id: int = Form(...)):
    # Logica di acquisto da implementare
    return templates.TemplateResponse("shop.html", {"request": request, "message": f"Acquisto completato per item {item_id}"})
