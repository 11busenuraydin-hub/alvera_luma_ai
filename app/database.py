
import os
import sqlite3

from pathlib import Path
from datetime import datetime, timezone

# Render'da kalıcı disk varsa:
# SQLITE_DIR=/var/data
#
# Yoksa proje içinde storage klasörü kullanılır.

BASE_DIR = Path(__file__).resolve().parent.parent

DB_DIR = Path(
    os.getenv("SQLITE_DIR", str(BASE_DIR / "storage"))
)

DB_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DB_DIR / "alvera.db"


def get_db():
    conn = sqlite3.connect(
        str(DB_PATH),
        timeout=30
    )

    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA busy_timeout = 30000")
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


def init_db():
    conn = get_db()

    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                adSoyad TEXT NOT NULL,
                telefon TEXT,
                eMail TEXT,
                mesaj TEXT NOT NULL,
                tarih TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_contacts_tarih
            ON contacts(tarih DESC)
        """)

        conn.commit()

        print(
            "[ALVERA SQLITE] Veritabanı hazır:",
            DB_PATH
        )

    finally:
        conn.close()


def add_contact(adSoyad, telefon, eMail, mesaj):
    conn = get_db()

    try:
        tarih = datetime.now(
            timezone.utc
        ).isoformat()

        cursor = conn.execute("""
            INSERT INTO contacts (
                adSoyad,
                telefon,
                eMail,
                mesaj,
                tarih
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            adSoyad,
            telefon,
            eMail,
            mesaj,
            tarih
        ))

        conn.commit()

        return cursor.lastrowid

    finally:
        conn.close()


def list_contacts(limit=100):
    conn = get_db()

    try:
        rows = conn.execute("""
            SELECT
                id,
                adSoyad,
                telefon,
                eMail,
                mesaj,
                tarih
            FROM contacts
            ORDER BY tarih DESC, id DESC
            LIMIT ?
        """, (limit,)).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:
        conn.close()


def contact_statistics():
    conn = get_db()

    try:
        total = conn.execute("""
            SELECT COUNT(*) FROM contacts
        """).fetchone()[0]

        rows = conn.execute("""
            SELECT adSoyad, telefon, eMail
            FROM contacts
        """).fetchall()

        customers = set()

        for row in rows:
            email = (
                row["eMail"] or ""
            ).strip().lower()

            telefon = (
                row["telefon"] or ""
            ).strip()

            ad = (
                row["adSoyad"] or ""
            ).strip().lower()

            key = email or telefon or ad

            if key:
                customers.add(key)

        return {
            "totalCount": total,
            "uniqueCustomers": len(customers)
        }

    finally:
        conn.close()
