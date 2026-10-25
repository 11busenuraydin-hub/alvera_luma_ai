
import os

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    func,
)
from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
)
from datetime import datetime, timezone

DATABASE_URL = os.environ["DATABASE_URL"]

# Render bağlantı adresi eski postgres:// formatında olabilir.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql://",
        1
    )

if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1
    )

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False
)

Base = declarative_base()


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True)
    adSoyad = Column(String(200), nullable=False)
    telefon = Column(String(40), nullable=True)
    eMail = Column(String(254), nullable=True)
    mesaj = Column(Text, nullable=False)
    tarih = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )


def init_db():
    Base.metadata.create_all(bind=engine)


def serialize_contact(kayit):
    return {
        "id": kayit.id,
        "adSoyad": kayit.adSoyad,
        "telefon": kayit.telefon,
        "eMail": kayit.eMail,
        "mesaj": kayit.mesaj,
        "tarih": (
            kayit.tarih.isoformat()
            if kayit.tarih else None
        )
    }


def count_customers(session):
    kayitlar = session.query(
        Contact.eMail,
        Contact.telefon,
        Contact.adSoyad
    ).all()

    musteriler = set()

    for email, telefon, ad in kayitlar:
        email = (email or "").strip().lower()
        telefon = (telefon or "").strip()
        ad = (ad or "").strip().lower()

        anahtar = email or telefon or ad

        if anahtar:
            musteriler.add(anahtar)

    return len(musteriler)
