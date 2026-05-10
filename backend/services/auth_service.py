"""Authentication business logic."""
import bcrypt
from models.user import UserModel


class AuthService:
    @staticmethod
    def hash_password(plain):
        return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify_password(plain, hashed):
        try:
            return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
        except (ValueError, TypeError):
            return False

    @staticmethod
    def register(name, email, password, phone=None, role="user"):
        existing = UserModel.find_by_email(email)
        if existing:
            return None, "Email already registered"
        password_hash = AuthService.hash_password(password)
        user_id = UserModel.create(name, email, password_hash, phone, role)
        return user_id, None

    @staticmethod
    def authenticate(email, password):
        user = UserModel.find_by_email(email)
        if not user:
            return None, "Invalid credentials"
        if not AuthService.verify_password(password, user["password_hash"]):
            return None, "Invalid credentials"
        return user, None
