"""Menu management: add, list, search and remove food items."""
from .validators import (ValidationError, validate_name, validate_category,
                         validate_price, validate_id)

ACTIVE_STATUSES = ("Placed", "Preparing", "Out for Delivery")


def add_item(conn, name, category, price):
    name = validate_name(name, "Item name")
    category = validate_category(category)
    price = validate_price(price)
    exists = conn.execute("SELECT 1 FROM menu_items WHERE name = ?", (name,)).fetchone()
    if exists:
        raise ValidationError("A menu item with this name already exists.")
    cur = conn.execute(
        "INSERT INTO menu_items (name, category, price) VALUES (?, ?, ?)",
        (name, category, price))
    conn.commit()
    return cur.lastrowid


def get_item(conn, item_id):
    item_id = validate_id(item_id, "Item ID")
    row = conn.execute("SELECT * FROM menu_items WHERE id = ?", (item_id,)).fetchone()
    if row is None:
        raise ValidationError(f"No menu item found with ID {item_id}.")
    return row


def list_items(conn, only_available=False):
    sql = "SELECT * FROM menu_items"
    if only_available:
        sql += " WHERE available = 1"
    return conn.execute(sql + " ORDER BY category, name").fetchall()


def search_items(conn, keyword):
    keyword = (keyword or "").strip()
    if not keyword:
        raise ValidationError("Search keyword cannot be empty.")
    like = f"%{keyword}%"
    return conn.execute(
        "SELECT * FROM menu_items WHERE name LIKE ? OR category LIKE ? ORDER BY name",
        (like, like)).fetchall()


def set_availability(conn, item_id, available):
    get_item(conn, item_id)
    conn.execute("UPDATE menu_items SET available = ? WHERE id = ?",
                 (1 if available else 0, item_id))
    conn.commit()


def remove_item(conn, item_id):
    item = get_item(conn, item_id)
    placeholders = ",".join("?" * len(ACTIVE_STATUSES))
    in_use = conn.execute(
        "SELECT 1 FROM order_items oi JOIN orders o ON o.id = oi.order_id "
        f"WHERE oi.menu_item_id = ? AND o.status IN ({placeholders})",
        (item["id"], *ACTIVE_STATUSES)).fetchone()
    if in_use:
        raise ValidationError("Item is part of an active order and cannot be removed.")
    ever_ordered = conn.execute(
        "SELECT 1 FROM order_items WHERE menu_item_id = ?", (item["id"],)).fetchone()
    if ever_ordered:
        # keep the row so old orders still show the item name; just hide it
        conn.execute("UPDATE menu_items SET available = 0 WHERE id = ?", (item["id"],))
    else:
        conn.execute("DELETE FROM menu_items WHERE id = ?", (item["id"],))
    conn.commit()
