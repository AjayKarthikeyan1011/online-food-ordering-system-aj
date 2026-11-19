"""Shopping cart with bill calculation."""
from . import menu
from .validators import ValidationError, MAX_QTY, validate_quantity, validate_id

TAX_RATE = 0.05
DELIVERY_FEE = 40.0
FREE_DELIVERY_ABOVE = 500.0


class Cart:
    """Holds menu item ids and quantities for one ordering session."""

    def __init__(self):
        self.items = {}

    def add(self, conn, item_id, quantity):
        item = menu.get_item(conn, item_id)
        quantity = validate_quantity(quantity)
        if not item["available"]:
            raise ValidationError(f"'{item['name']}' is currently not available.")
        new_qty = self.items.get(item["id"], 0) + quantity
        if new_qty > MAX_QTY:
            raise ValidationError(f"You can order at most {MAX_QTY} of one item.")
        self.items[item["id"]] = new_qty

    def remove(self, item_id):
        item_id = validate_id(item_id, "Item ID")
        if item_id not in self.items:
            raise ValidationError("That item is not in your cart.")
        del self.items[item_id]

    def clear(self):
        self.items.clear()

    def is_empty(self):
        return not self.items

    def lines(self, conn):
        """Return a list of (item row, quantity, line amount)."""
        result = []
        for item_id, qty in self.items.items():
            item = menu.get_item(conn, item_id)
            result.append((item, qty, round(item["price"] * qty, 2)))
        return result

    def totals(self, conn):
        subtotal = round(sum(amount for _, _, amount in self.lines(conn)), 2)
        tax = round(subtotal * TAX_RATE, 2)
        delivery = 0.0 if subtotal == 0 or subtotal >= FREE_DELIVERY_ABOVE else DELIVERY_FEE
        return {"subtotal": subtotal, "tax": tax, "delivery_fee": delivery,
                "total": round(subtotal + tax + delivery, 2)}
