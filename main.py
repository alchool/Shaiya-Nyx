from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import pyodbc
import os

# -----------------------
# CONFIGURAZIONE APP
# -----------------------
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="CAMBIA_QUESTA_CHIAVE", max_age=3600)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# -----------------------
# CONNESSIONE DB
# -----------------------
def get_db_connection():
    return pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={os.getenv('DB_HOST','localhost')};"
        f"DATABASE={os.getenv('DB_NAME','PS_GameData')};"
        f"UID={os.getenv('DB_USER','sa')};"
        f"PWD={os.getenv('DB_PASSWORD','password')}"
    )

# -----------------------
# AUTENTICAZIONE
# -----------------------
def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=status.HTTP_302_FOUND, headers={"Location": "/login"})
    return user

# -----------------------
# ROUTES PUBBLICHE
# -----------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register_post(username: str = Form(...), password: str = Form(...), email: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO PS_UserData.dbo.Users_Master (UserID, Pw, Email) 
        VALUES (?, ?, ?)
    """, (username, password, email))
    conn.commit()
    cursor.close()
    conn.close()
    return RedirectResponse(url="/login", status_code=302)

@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT UserID FROM PS_UserData.dbo.Users_Master
        WHERE UserID=? AND Pw=?
    """, (username, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        request.session["user"] = username
        return RedirectResponse(url="/profile", status_code=302)
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Credenziali non valide"})

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)

# -----------------------
# ROUTES PROTETTE
# -----------------------
@app.get("/profile", response_class=HTMLResponse)
def profile(request: Request, current_user: str = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TOP 1 Email, K1, Exp, Point 
        FROM PS_UserData.dbo.Users_Master U
        JOIN PS_GameData.dbo.Chars C ON U.UserUID = C.UserUID
        WHERE UserID = ?
    """, (current_user,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row:
        user = {
            "username": current_user,
            "email": row.Email,
            "kills": row.K1,
            "exp": row.Exp,
            "ap": row.Point
        }
        inventory = []  # Placeholder per /inventory
        return templates.TemplateResponse("profile.html", {"request": request, "user": user, "inventory": inventory})
    else:
        return RedirectResponse(url="/login", status_code=302)

@app.get("/pvp_rankings", response_class=HTMLResponse)
def pvp_rankings(request: Request, current_user: str = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TOP 50 CharName, K1 AS Kills
        FROM PS_GameData.dbo.Chars
        ORDER BY K1 DESC
    """)
    rankings = cursor.fetchall()
    cursor.close()
    conn.close()
    return templates.TemplateResponse("pvp_rankings.html", {"request": request, "rankings": rankings})

@app.get("/inventory", response_class=HTMLResponse)
def inventory(request: Request, current_user: str = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT Slot, ItemName, Count
        FROM PS_GameData.dbo.CharItems CI
        JOIN PS_GameDefs.dbo.ItemsDefs ID ON CI.ItemID = ID.ItemID
        WHERE CharID IN (
            SELECT CharID FROM PS_GameData.dbo.Chars 
            WHERE UserID = ?
        )
    """, (current_user,))
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    return templates.TemplateResponse("inventory.html", {"request": request, "items": items})

@app.get("/shop", response_class=HTMLResponse)
def shop(request: Request, current_user: str = Depends(get_current_user)):
    return templates.TemplateResponse("shop.html", {"request": request})
