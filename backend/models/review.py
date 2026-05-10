"""Review model."""
from extensions import get_cursor


class ReviewModel:
    @staticmethod
    def list_for_product(product_id):
        with get_cursor() as cur:
            cur.execute(
                "SELECT r.id, r.rating, r.comment, r.created_at, u.name AS user_name "
                "FROM reviews r JOIN users u ON u.id = r.user_id "
                "WHERE r.product_id = %s ORDER BY r.created_at DESC",
                (product_id,),
            )
            return cur.fetchall()

    @staticmethod
    def create(user_id, product_id, rating, comment):
        with get_cursor(commit=True) as cur:
            cur.execute(
                "INSERT INTO reviews (user_id, product_id, rating, comment) "
                "VALUES (%s, %s, %s, %s) "
                "ON DUPLICATE KEY UPDATE rating = VALUES(rating), "
                "comment = VALUES(comment)",
                (user_id, product_id, rating, comment),
            )
            return cur.lastrowid or True
