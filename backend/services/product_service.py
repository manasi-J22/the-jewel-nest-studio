"""Product image upload and product helpers."""
import os
import uuid
from werkzeug.utils import secure_filename
from config import Config


class ProductService:
    @staticmethod
    def allowed_file(filename):
        if "." not in filename:
            return False
        ext = filename.rsplit(".", 1)[1].lower()
        return ext in Config.ALLOWED_EXTENSIONS

    @staticmethod
    def save_image(file_storage):
        if not file_storage or file_storage.filename == "":
            return None
        if not ProductService.allowed_file(file_storage.filename):
            raise ValueError("File type not allowed")
        ext = file_storage.filename.rsplit(".", 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        secure = secure_filename(filename)
        upload_dir = Config.UPLOAD_FOLDER
        os.makedirs(upload_dir, exist_ok=True)
        path = os.path.join(upload_dir, secure)
        file_storage.save(path)
        return f"/uploads/{secure}"
