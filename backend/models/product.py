"""Product model."""
from extensions import get_cursor


class ProductModel:
    @staticmethod
    def list_filtered(category=None, min_price=None, max_price=None,
                      search=None, sort="newest", limit=50, offset=0):
        sql = (
            "SELECT p.id, p.name, p.description, p.price, p.category, p.material, "
            "p.stock, p.image_url, p.created_at, "
            "COALESCE(AVG(r.rating), 0) AS avg_rating, COUNT(r.id) AS review_count "
            "FROM products p LEFT JOIN reviews r ON r.product_id = p.id "
            "WHERE 1=1 "
        )
        params = []
        if category:
            sql += "AND p.category = %s "
            params.append(category)
        if min_price is not None:
            sql += "AND p.price >= %s "
            params.append(min_price)
        if max_price is not None:
            sql += "AND p.price <= %s "
            params.append(max_price)
        if search:
            sql += "AND (p.name LIKE %s OR p.description LIKE %s) "
            params.extend([f"%{search}%", f"%{search}%"])

        sql += "GROUP BY p.id "
        order_map = {
            "price_asc": "p.price ASC",
            "price_desc": "p.price DESC",
            "rating": "avg_rating DESC",
            "newest": "p.created_at DESC",
        }
        sql += f"ORDER BY {order_map.get(sort, 'p.created_at DESC')} "
        sql += "LIMIT %s OFFSET %s"
        params.extend([int(limit), int(offset)])

        with get_cursor() as cur:
            cur.execute(sql, tuple(params))
            return cur.fetchall()

    @staticmethod
    def get(product_id):
        with get_cursor() as cur:
            cur.execute(
                "SELECT p.id, p.name, p.description, p.price, p.category, p.material, "
                "p.stock, p.image_url, p.created_at, "
                "COALESCE(AVG(r.rating), 0) AS avg_rating, COUNT(r.id) AS review_count "
                "FROM products p LEFT JOIN reviews r ON r.product_id = p.id "
                "WHERE p.id = %s GROUP BY p.id",
                (product_id,),
            )
            return cur.fetchone()

    @staticmethod
    def categories():
        with get_cursor() as cur:
            cur.execute("SELECT DISTINCT category FROM products ORDER BY category")
            return [row["category"] for row in cur.fetchall()]

    @staticmethod
    def create(data):
        with get_cursor(commit=True) as cur:
            cur.execute(
                "INSERT INTO products (name, description, price, category, material, "
                "stock, image_url) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (
                    data["name"], data.get("description"), data["price"],
                    data["category"], data.get("material"),
                    data.get("stock", 0), data.get("image_url"),
                ),
            )
            return cur.lastrowid

    @staticmethod
    def update(product_id, data):
        fields, params = [], []
        for key in ("name", "description", "price", "category", "material",
                    "stock", "image_url"):
            if key in data:
                fields.append(f"{key} = %s")
                params.append(data[key])
        if not fields:
            return False
        params.append(product_id)
        sql = f"UPDATE products SET {', '.join(fields)} WHERE id = %s"
        with get_cursor(commit=True) as cur:
            cur.execute(sql, tuple(params))
            return cur.rowcount > 0

    @staticmethod
    def delete(product_id):
        with get_cursor(commit=True) as cur:
            cur.execute("DELETE FROM products WHERE id = %s", (product_id,))
            return cur.rowcount > 0

    @staticmethod
    def decrement_stock(product_id, qty, cursor):
        cursor.execute(
            "UPDATE products SET stock = stock - %s WHERE id = %s AND stock >= %s",
            (qty, product_id, qty),
        )
        return cursor.rowcount > 0
