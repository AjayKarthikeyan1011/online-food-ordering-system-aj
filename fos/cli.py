"""Interactive command-line menu for the Online Food Ordering System."""
import sys

from . import cart as cart_module
from . import customers, menu, orders
from .database import connect
from .validators import ValidationError

MENU_TEXT = """
========== ONLINE FOOD ORDERING SYSTEM ==========
  1. Add menu item          8. View cart
  2. List menu              9. Remove item from cart
  3. Search menu           10. Place order
  4. Remove menu item      11. Order history
  5. Register customer     12. Update order status
  6. List customers        13. Cancel order
  7. Add item to cart       0. Exit
  (type m to show this menu again)
=================================================""".strip("\n")


def ask(prompt):
    """Read one line; echo it when input is piped so transcripts stay readable."""
    value = input(prompt)
    if not sys.stdin.isatty():
        print(value)
    return value


def show_menu_items(rows):
    if not rows:
        print("No menu items found.")
        return
    print(f"{'ID':<4}{'Item':<22}{'Category':<14}{'Price':>8}  Status")
    for r in rows:
        status = "Available" if r["available"] else "Unavailable"
        print(f"{r['id']:<4}{r['name']:<22}{r['category']:<14}{r['price']:>8.2f}  {status}")


def show_cart(conn, cart):
    lines = cart.lines(conn)
    if not lines:
        print("Your cart is empty.")
        return
    print(f"{'ID':<4}{'Item':<22}{'Qty':>4}{'Price':>9}{'Amount':>10}")
    for item, qty, amount in lines:
        print(f"{item['id']:<4}{item['name']:<22}{qty:>4}{item['price']:>9.2f}{amount:>10.2f}")
    t = cart.totals(conn)
    print(f"Subtotal : Rs. {t['subtotal']:.2f}")
    print(f"GST (5%) : Rs. {t['tax']:.2f}")
    print(f"Delivery : Rs. {t['delivery_fee']:.2f}")
    print(f"Total    : Rs. {t['total']:.2f}")


def show_orders(conn, rows):
    if not rows:
        print("No orders found.")
        return
    for o in rows:
        print(f"Order #{o['id']} | {o['customer_name']} | {o['status']} | "
              f"{o['created_at']} | Total Rs. {o['total']:.2f}")
        items = ", ".join(f"{l['quantity']} x {l['name']}" for l in orders.order_lines(conn, o["id"]))
        print(f"   {items}")


def handle(choice, conn, cart):
    if choice == "1":
        name = ask("Item name: ")
        category = ask("Category (Starters/Main Course/Desserts/Drinks): ")
        price = ask("Price (Rs.): ")
        print(f"Menu item added with ID {menu.add_item(conn, name, category, price)}.")
    elif choice == "2":
        show_menu_items(menu.list_items(conn))
    elif choice == "3":
        show_menu_items(menu.search_items(conn, ask("Keyword (name/category): ")))
    elif choice == "4":
        menu.remove_item(conn, ask("Item ID to remove: "))
        print("Menu item removed.")
    elif choice == "5":
        name = ask("Name: ")
        email = ask("Email: ")
        phone = ask("Phone (10 digits): ")
        print(f"Customer registered with ID {customers.register_customer(conn, name, email, phone)}.")
    elif choice == "6":
        rows = customers.list_customers(conn)
        print(f"{'ID':<4}{'Name':<22}{'Email':<28}Phone")
        for c in rows:
            print(f"{c['id']:<4}{c['name']:<22}{c['email']:<28}{c['phone']}")
    elif choice == "7":
        item_id = ask("Item ID: ")
        qty = ask("Quantity: ")
        cart.add(conn, item_id, qty)
        print("Item added to cart.")
    elif choice == "8":
        show_cart(conn, cart)
    elif choice == "9":
        cart.remove(ask("Item ID to remove from cart: "))
        print("Item removed from cart.")
    elif choice == "10":
        order_id = orders.place_order(conn, ask("Customer ID: "), cart)
        order = orders.get_order(conn, order_id)
        print(f"Order placed. Order ID {order_id}, total Rs. {order['total']:.2f}.")
    elif choice == "11":
        show_orders(conn, orders.order_history(conn, ask("Customer ID: ")))
    elif choice == "12":
        old, new = orders.update_status(conn, ask("Order ID: "))
        print(f"Order status updated: {old} -> {new}.")
    elif choice == "13":
        orders.cancel_order(conn, ask("Order ID: "))
        print("Order cancelled.")
    elif choice.lower() == "m":
        print(MENU_TEXT)
    else:
        raise ValidationError("Invalid choice. Enter m to show the menu.")


def run(db_path="food_ordering.db"):
    conn = connect(db_path)
    cart = cart_module.Cart()
    print(MENU_TEXT)
    try:
        while True:
            choice = ask("Enter choice: ").strip()
            if choice == "0":
                print("Goodbye!")
                break
            try:
                handle(choice, conn, cart)
            except ValidationError as error:
                print(f"Error: {error}")
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
    finally:
        conn.close()
