from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import pyodbc
import os
import secrets
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta

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

# Memoria temporanea per token reset
reset_tokens = {}

# -----------------------
# RESET PASSWORD - STEP 1
# -----------------------
@app.get("/reset_password", response_class=HTMLResponse)
def reset_password_form(request: Request):
    return templates.TemplateResponse("reset_password.html", {"request": request})

@app.post("/reset_password")
def reset_password_request(email: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT UserID FROM PS_UserData.dbo.Users_Master WHERE Email=?
    """, (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        return {"error": "Email non trovata"}

    token = secrets.token_urlsafe(32)
    expire_time = datetime.utcnow() + timedelta(hours=1)
    reset_tokens[token] = {"user": user.UserID, "expire": expire_time}

    reset_link = f"http://localhost:8000/reset_password_confirm?token={token}"
    send_reset_email(email, reset_link)

    return {"message": "Se l'email è corretta, riceverai un link per il reset."}

# -----------------------
# RESET PASSWORD - STEP 2
# -----------------------
@app.get("/reset_password_confirm", response_class=HTMLResponse)
def reset_password_confirm(request: Request, token: str):
    if token not in reset_tokens or datetime.utcnow() > reset_tokens[token]["expire"]:
        return {"error": "Token scaduto o non valido"}
    return templates.TemplateResponse("reset_password_confirm.html", {"request": request, "token": token})

@app.post("/reset_password_confirm")
def reset_password_update(token: str = Form(...), new_password: str = Form(...)):
    if token not in reset_tokens or datetime.utcnow() > reset_tokens[token]["expire"]:
        return {"error": "Token scaduto o non valido"}

    username = reset_tokens[token]["user"]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE PS_UserData.dbo.Users_Master SET Pw=? WHERE UserID=?
    """, (new_password, username))
    conn.commit()
    cursor.close()
    conn.close()

    del reset_tokens[token]
    return RedirectResponse(url="/login", status_code=302)

# -----------------------
# FUNZIONE INVIO EMAIL
# -----------------------
def send_reset_email(to_email: str, reset_link: str):
    smtp_server = os.getenv("SMTP_SERVER", "smtp.example.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER", "noreply@example.com")
    smtp_password = os.getenv("SMTP_PASSWORD", "password")

    msg = MIMEText(f"Clicca qui per resettare la tua password: {reset_link}")
    msg["Subject"] = "Reset Password - Shaiya Server"
    msg["From"] = smtp_user
    msg["To"] = to_email

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)

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
