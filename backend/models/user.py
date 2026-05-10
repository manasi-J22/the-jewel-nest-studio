"""User model — raw SQL data access."""
from extensions import get_cursor


class UserModel:
    @staticmethod
    def find_by_email(email):
        with get_cursor() as cur:
            cur.execute(
                "SELECT id, name, email, password_hash, phone, role, created_at "
                "FROM users WHERE email = %s",
                (email,),
            )
            return cur.fetchone()

    @staticmethod
    def find_by_id(user_id):
        with get_cursor() as cur:
            cur.execute(
                "SELECT id, name, email, phone, role, created_at "
                "FROM users WHERE id = %s",
                (user_id,),
            )
            return cur.fetchone()

    @staticmethod
    def create(name, email, password_hash, phone=None, role="user"):
        with get_cursor(commit=True) as cur:
            cur.execute(
                "INSERT INTO users (name, email, password_hash, phone, role) "
                "VALUES (%s, %s, %s, %s, %s)",
                (name, email, password_hash, phone, role),
            )
            return cur.lastrowid

    @staticmethod
    def list_all():
        with get_cursor() as cur:
            cur.execute(
                "SELECT id, name, email, phone, role, created_at "
                "FROM users ORDER BY created_at DESC"
            )
            return cur.fetchall()
