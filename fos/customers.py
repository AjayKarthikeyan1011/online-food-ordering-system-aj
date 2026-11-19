"""Customer registration and lookup."""
from .validators import (ValidationError, validate_name, validate_email,
                         validate_phone, validate_id)


def register_customer(conn, name, email, phone):
    name = validate_name(name)
    email = validate_email(email)
    phone = validate_phone(phone)
    if conn.execute("SELECT 1 FROM customers WHERE email = ?", (email,)).fetchone():
        raise ValidationError("A customer with this email is already registered.")
    cur = conn.execute("INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)",
                       (name, email, phone))
    conn.commit()
    return cur.lastrowid


def get_customer(conn, customer_id):
    customer_id = validate_id(customer_id, "Customer ID")
    row = conn.execute("SELECT * FROM customers WHERE id = ?", (customer_id,)).fetchone()
    if row is None:
        raise ValidationError(f"No customer found with ID {customer_id}.")
    return row


def list_customers(conn):
    return conn.execute("SELECT * FROM customers ORDER BY id").fetchall()
