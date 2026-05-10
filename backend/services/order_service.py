"""Order checkout business logic."""
from decimal import Decimal
from models.product import ProductModel
from models.order import OrderModel


class OrderService:
    @staticmethod
    def checkout(user_id, cart, address, phone, payment_method):
        """cart: list of {product_id, quantity}. Returns (order_id, error)."""
        if not cart:
            return None, "Cart is empty"

        items, total = [], Decimal("0.00")
        for entry in cart:
            product = ProductModel.get(entry["product_id"])
            if not product:
                return None, f"Product {entry['product_id']} not found"
            qty = int(entry["quantity"])
            if qty < 1:
                return None, "Invalid quantity"
            if product["stock"] < qty:
                return None, f"Insufficient stock for '{product['name']}'"
            unit_price = Decimal(str(product["price"]))
            total += unit_price * qty
            items.append({
                "product_id": product["id"],
                "name": product["name"],
                "quantity": qty,
                "unit_price": unit_price,
            })

        try:
            order_id = OrderModel.create_with_items(
                user_id, items, total, address, phone, payment_method
            )
        except ValueError as e:
            return None, str(e)
        return order_id, None
