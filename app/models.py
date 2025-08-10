from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.sql import func
from .db import Base
from .database import Base  # o come si chiama il file di base

# Mappatura semplificata delle tabelle principali di Shaiya.
class UserMaster(Base):
    __tablename__ = 'Users_Master'  # verificare nome esatto nel vostro DB
    UserNo = Column(Integer, primary_key=True, index=True)
    UserID = Column(String(50), unique=True, index=True, nullable=False)
    Pw = Column(String(255), nullable=False)
    Email = Column(String(255))
    Point = Column(Integer, default=0)  # AP
    Status = Column(Integer, default=0)
    RegDate = Column(DateTime, server_default=func.now())

class User(Base):
    __tablename__ = 'Users_Master'
    __table_args__ = {'schema': 'dbo'}

    UserUID = Column(Integer, primary_key=True, autoincrement=True)
    UserID = Column(String(50), unique=True, nullable=False)
    Pw = Column(String(255), nullable=False)
    Email = Column(String(255), nullable=False)
    Point = Column(Integer, default=0)

    # Relazioni (esempio, se necessario)
    donations = relationship("DonationLog", back_populates="user")

class Char(Base):
    __tablename__ = 'Chars'  # verificare schema e nome
    CharID = Column(Integer, primary_key=True)
    UserNo = Column(Integer, index=True)
    Name = Column(String(50), index=True)
    Level = Column(Integer, default=1)
    Exp = Column(Integer, default=0)
    K1 = Column(Integer, default=0)
    K2 = Column(Integer, default=0)
    K3 = Column(Integer, default=0)
    K4 = Column(Integer, default=0)

class Inventory(Base):
    __tablename__ = 'Inventory'
    # struttura dipende dal vostro DB; adattare di conseguenza
    InvID = Column(Integer, primary_key=True)
    CharID = Column(Integer, index=True)
    ItemID = Column(Integer)
    Count = Column(Integer, default=1)

class DonationLog(Base):
    __tablename__ = "Donation_Log"
    __table_args__ = {"schema": "dbo"}  # importante con SQL Server

    ID = Column(Integer, primary_key=True, index=True)
    UserUID = Column(Integer, nullable=False)
    UserID = Column(String(50), nullable=False)
    AmountUSD = Column(DECIMAL(10, 2), nullable=False)
    APGranted = Column(Integer, nullable=False)
    PayPalTxnID = Column(String(255), nullable=False)
    Status = Column(String(50), nullable=False)
    CreatedAt = Column(DateTime(timezone=True), server_default=func.now())

    # Relazione con User
    user = relationship("User", back_populates="donations")
