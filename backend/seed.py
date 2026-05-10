"""Seed script — creates schema and inserts sample data.

Run:
    python seed.py
"""
import os
import sys
from datetime import date, timedelta

import mysql.connector
from dotenv import load_dotenv

load_dotenv()

from services.auth_service import AuthService  # noqa: E402

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
DB_NAME = os.getenv("DB_NAME", "jewelry_store")

SAMPLE_PRODUCTS = [
    {
        "name": "Eternal Solitaire Diamond Ring",
        "description": "An 18k white gold solitaire ring with a brilliant-cut "
                       "0.5ct diamond. A timeless symbol of love.",
        "price": 1499.00, "category": "Rings", "material": "18k White Gold",
        "stock": 12,
        "image_url": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=800",
    },
    {
        "name": "Pearl Cascade Necklace",
        "description": "Hand-knotted freshwater pearls with a 14k gold clasp. "
                       "Lustrous, elegant, evening-perfect.",
        "price": 599.00, "category": "Necklaces", "material": "Pearl & Gold",
        "stock": 20,
        "image_url": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=800",
    },
    {
        "name": "Sapphire Halo Earrings",
        "description": "Royal blue sapphires haloed by pavé diamonds, set in "
                       "platinum. Subtle drama for any occasion.",
        "price": 1299.00, "category": "Earrings", "material": "Platinum",
        "stock": 8,
        "image_url": "https://images.unsplash.com/photo-1635767582909-345b16f1ee99?w=800",
    },
    {
        "name": "Rose Gold Tennis Bracelet",
        "description": "A continuous line of round-cut diamonds in 18k rose "
                       "gold. Refined sparkle on the wrist.",
        "price": 2199.00, "category": "Bracelets", "material": "18k Rose Gold",
        "stock": 6,
        "image_url": "https://images.unsplash.com/photo-1611652022419-a9419f74343d?w=800",
    },
    {
        "name": "Emerald Vine Pendant",
        "description": "A Colombian emerald set in a delicate diamond vine "
                       "pendant. Lush, romantic, one-of-a-kind.",
        "price": 899.00, "category": "Necklaces", "material": "18k Yellow Gold",
        "stock": 10,
        "image_url": "https://images.unsplash.com/photo-1611591437281-460bfbe1220a?w=800",
    },
    {
        "name": "Twisted Vine Wedding Band",
        "description": "Hand-crafted twisted vine band with micro-pavé "
                       "diamonds. A modern heirloom.",
        "price": 749.00, "category": "Rings", "material": "14k Yellow Gold",
        "stock": 15,
        "image_url": "https://images.unsplash.com/photo-1602173574767-37ac01994b2a?w=800",
    },
    {
        "name": "Diamond Drop Earrings",
        "description": "Elegant drop earrings with cascading diamonds. Light "
                       "catches every movement.",
        "price": 1099.00, "category": "Earrings", "material": "18k White Gold",
        "stock": 9,
        "image_url": "https://images.unsplash.com/photo-1535632787350-4e68ef0ac584?w=800",
    },
    {
        "name": "Ruby Heart Pendant",
        "description": "A 1ct heart-cut ruby surrounded by diamonds. "
                       "Romance distilled into a single piece.",
        "price": 1799.00, "category": "Necklaces", "material": "18k Yellow Gold",
        "stock": 5,
        "image_url": "https://images.unsplash.com/photo-1586878341523-7c3eb9b66021?w=800",
    },
    {
        "name": "Minimalist Gold Bangle",
        "description": "A sleek 14k gold bangle. Effortless to stack or "
                       "wear alone.",
        "price": 449.00, "category": "Bracelets", "material": "14k Gold",
        "stock": 25,
        "image_url": "https://images.unsplash.com/photo-1573408301185-9146fe634ad0?w=800",
    },
    {
        "name": "Vintage Art-Deco Ring",
        "description": "Geometric Art-Deco styling with sapphires and "
                       "diamonds. A statement of vintage glamour.",
        "price": 1599.00, "category": "Rings", "material": "Platinum",
        "stock": 4,
        "image_url": "https://images.unsplash.com/photo-1603561591411-07134e71a2a9?w=800",
    },
    {
        "name": "Hoop Earrings — Pavé Diamond",
        "description": "Classic medium hoops set with pavé diamonds. "
                       "An everyday luxury.",
        "price": 699.00, "category": "Earrings", "material": "18k White Gold",
        "stock": 14,
        "image_url": "https://images.unsplash.com/photo-1630019852942-f89202989a59?w=800",
    },
    {
        "name": "Charm Bracelet — Celestial",
        "description": "Sun, moon and star charms in 14k gold on a delicate "
                       "chain. Personal and playful.",
        "price": 549.00, "category": "Bracelets", "material": "14k Gold",
        "stock": 18,
        "image_url": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=800",
    },
]


def main():
    print(f"Connecting to MySQL at {DB_HOST}:{DB_PORT}…")
    try:
        server = mysql.connector.connect(
            host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD
        )
        cur = server.cursor()
        cur.execute(
            f"CREATE DATABASE IF NOT EXISTS {DB_NAME} "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        server.commit()
        cur.close()
        server.close()
    except mysql.connector.Error as e:
        # Managed MySQL (Clever Cloud, PlanetScale, etc.) often denies
        # CREATE DATABASE — the user only has rights to a pre-provisioned
        # DB. Skip and continue; we'll use whatever DB_NAME points at.
        if e.errno in (1044, 1045, 1046):
            print(f"  (skipping CREATE DATABASE: {e.msg}) — using existing DB {DB_NAME}")
        else:
            raise

    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    conn = mysql.connector.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER,
        password=DB_PASSWORD, database=DB_NAME,
    )
    cur = conn.cursor()
    print("Applying schema…")

    def strip_sql_comments(stmt):
        # Drop -- line comments so we can inspect the real first keyword.
        lines = [ln for ln in stmt.splitlines() if not ln.strip().startswith("--")]
        return "\n".join(lines).strip()

    for raw in schema_sql.split(";"):
        stmt = strip_sql_comments(raw)
        if not stmt:
            continue
        if stmt.lower().startswith(("create database", "use ")):
            continue
        cur.execute(stmt)
    conn.commit()

    print("Seeding admin and demo users…")
    admin_hash = AuthService.hash_password("Admin@123")
    demo_hash = AuthService.hash_password("Demo@123")
    cur.execute(
        "INSERT IGNORE INTO users (name, email, password_hash, role) "
        "VALUES (%s, %s, %s, 'admin')",
        ("Store Admin", "admin@jewel.com", admin_hash),
    )
    cur.execute(
        "INSERT IGNORE INTO users (name, email, password_hash, role) "
        "VALUES (%s, %s, %s, 'user')",
        ("Demo Customer", "demo@jewel.com", demo_hash),
    )
    conn.commit()

    print("Seeding products…")
    cur.execute("SELECT COUNT(*) FROM products")
    if cur.fetchone()[0] == 0:
        for p in SAMPLE_PRODUCTS:
            cur.execute(
                "INSERT INTO products (name, description, price, category, "
                "material, stock, image_url) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (p["name"], p["description"], p["price"], p["category"],
                 p["material"], p["stock"], p["image_url"]),
            )
        conn.commit()
    else:
        print("Products already present — skipping.")

    print("Seeding sample expenses…")
    cur.execute("SELECT COUNT(*) FROM expenses")
    if cur.fetchone()[0] == 0:
        today = date.today()
        samples = [
            ("Rent", 1200.00, today.replace(day=1), "Storefront monthly rent"),
            ("Utilities", 230.00, today.replace(day=3), "Electricity & water"),
            ("Marketing", 480.00, today.replace(day=10), "Instagram ads"),
            ("Inventory", 5400.00, today - timedelta(days=20), "New gold stock"),
            ("Salary", 3500.00, today.replace(day=28) - timedelta(days=30),
             "Staff payroll"),
        ]
        for s in samples:
            cur.execute(
                "INSERT INTO expenses (expense_type, amount, expense_date, note) "
                "VALUES (%s, %s, %s, %s)", s,
            )
        conn.commit()

    cur.close()
    conn.close()
    print("\n✓ Seed complete.")
    print("  Admin login:  admin@jewel.com / Admin@123")
    print("  User login:   demo@jewel.com  / Demo@123")


if __name__ == "__main__":
    sys.exit(main() or 0)
