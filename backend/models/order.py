"""Order model — handles orders and order items together."""


class OrderModel:
    @staticmethod
    def create_with_items(user_id, items, total, address, phone, payment_method):
        """Create an order plus items in a single transaction.
        items: list of dicts with product_id, quantity, unit_price, name"""
        conn = None
        try:
            from extensions import init_db_pool
            pool = init_db_pool()
            conn = pool.get_connection()
            cur = conn.cursor(dictionary=True)

            cur.execute(
                "INSERT INTO orders (user_id, total, status, address, phone, "
                "payment_method) VALUES (%s, %s, %s, %s, %s, %s)",
                (user_id, total, "pending", address, phone, payment_method),
            )
            order_id = cur.lastrowid

            for item in items:
                cur.execute(
                    "UPDATE products SET stock = stock - %s "
                    "WHERE id = %s AND stock >= %s",
                    (item["quantity"], item["product_id"], item["quantity"]),
                )
                if cur.rowcount == 0:
                    raise ValueError(
                        f"Insufficient stock for product {item['product_id']}"
                    )

                cur.execute(
                    "INSERT INTO order_items (order_id, product_id, product_name, "
                    "quantity, unit_price) VALUES (%s, %s, %s, %s, %s)",
                    (order_id, item["product_id"], item["name"],
                     item["quantity"], item["unit_price"]),
                )
            conn.commit()
            return order_id
        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    @staticmethod
    def list_for_user(user_id):
        from extensions import get_cursor
        with get_cursor() as cur:
            cur.execute(
                "SELECT id, total, status, address, phone, payment_method, "
                "created_at FROM orders WHERE user_id = %s "
                "ORDER BY created_at DESC",
                (user_id,),
            )
            orders = cur.fetchall()
            for order in orders:
                cur.execute(
                    "SELECT product_id, product_name, quantity, unit_price "
                    "FROM order_items WHERE order_id = %s",
                    (order["id"],),
                )
                order["items"] = cur.fetchall()
            return orders

    @staticmethod
    def list_all():
        from extensions import get_cursor
        with get_cursor() as cur:
            cur.execute(
                "SELECT o.id, o.user_id, u.name AS user_name, u.email AS user_email, "
                "o.total, o.status, o.address, o.phone, o.payment_method, o.created_at "
                "FROM orders o JOIN users u ON u.id = o.user_id "
                "ORDER BY o.created_at DESC"
            )
            orders = cur.fetchall()
            for order in orders:
                cur.execute(
                    "SELECT product_id, product_name, quantity, unit_price "
                    "FROM order_items WHERE order_id = %s",
                    (order["id"],),
                )
                order["items"] = cur.fetchall()
            return orders

    @staticmethod
    def update_status(order_id, status):
        from extensions import get_cursor
        with get_cursor(commit=True) as cur:
            cur.execute(
                "UPDATE orders SET status = %s WHERE id = %s",
                (status, order_id),
            )
            return cur.rowcount > 0
