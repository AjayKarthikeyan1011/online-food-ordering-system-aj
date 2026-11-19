"""Order placement, history and tracking."""
from datetime import datetime

from . import customers
from .validators import ValidationError, validate_id

STATUS_FLOW = ("Placed", "Preparing", "Out for Delivery", "Delivered")


def place_order(conn, customer_id, cart):
    customers.get_customer(conn, customer_id)
    if cart.is_empty():
        raise ValidationError("Your cart is empty. Add items before placing an order.")
    lines = cart.lines(conn)
    for item, _, _ in lines:
        if not item["available"]:
            raise ValidationError(f"'{item['name']}' is no longer available.")
    totals = cart.totals(conn)
    cur = conn.execute(
        "INSERT INTO orders (customer_id, subtotal, tax, delivery_fee, total, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (customer_id, totals["subtotal"], totals["tax"], totals["delivery_fee"],
         totals["total"], datetime.now().strftime("%Y-%m-%d %H:%M")))
    order_id = cur.lastrowid
    for item, qty, _ in lines:
        conn.execute(
            "INSERT INTO order_items (order_id, menu_item_id, quantity, unit_price) "
            "VALUES (?, ?, ?, ?)", (order_id, item["id"], qty, item["price"]))
    conn.commit()
    cart.clear()
    return order_id


def get_order(conn, order_id):
    order_id = validate_id(order_id, "Order ID")
    row = conn.execute(
        "SELECT o.*, c.name AS customer_name FROM orders o "
        "JOIN customers c ON c.id = o.customer_id WHERE o.id = ?", (order_id,)).fetchone()
    if row is None:
        raise ValidationError(f"No order found with ID {order_id}.")
    return row


def order_lines(conn, order_id):
    return conn.execute(
        "SELECT m.name, oi.quantity, oi.unit_price FROM order_items oi "
        "JOIN menu_items m ON m.id = oi.menu_item_id WHERE oi.order_id = ?",
        (order_id,)).fetchall()


def order_history(conn, customer_id):
    customers.get_customer(conn, customer_id)
    return conn.execute(
        "SELECT o.*, c.name AS customer_name FROM orders o "
        "JOIN customers c ON c.id = o.customer_id "
        "WHERE o.customer_id = ? ORDER BY o.id", (customer_id,)).fetchall()
