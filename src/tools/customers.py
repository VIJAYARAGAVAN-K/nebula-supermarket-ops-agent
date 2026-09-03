from src.database import get_connection
from datetime import datetime


def add_customer(name, phone=None):
    conn = get_connection()

    try:
        conn.execute(
            "INSERT INTO customers (name, phone) VALUES (?, ?)",
            (name, phone)
        )
        conn.commit()
        return f"Customer {name} added successfully."

    except Exception as e:
        conn.rollback()
        return f"Could not add customer: {e}"

    finally:
        conn.close()


def add_credit(customer_name, amount):
    if amount <= 0:
        return "Amount must be greater than zero."

    conn = get_connection()

    customer = conn.execute(
        "SELECT id FROM customers WHERE name LIKE ?",
        (f"%{customer_name}%",)
    ).fetchone()

    if not customer:
        conn.close()
        return "Customer not found."

    conn.execute(
        """INSERT INTO khata
        (customer_id, amount, type, created_at)
        VALUES (?, ?, ?, ?)""",
        (customer[0], amount, "credit", datetime.now().isoformat())
    )

    conn.commit()
    conn.close()

    return f"₹{amount:.2f} credit added for {customer_name}."

def add_payment(customer_name, amount):
    if amount <= 0:
        return "Amount must be greater than zero."

    conn = get_connection()

    customer = conn.execute(
        "SELECT id FROM customers WHERE name LIKE ?",
        (f"%{customer_name}%",)
    ).fetchone()

    if not customer:
        conn.close()
        return "Customer not found."

    conn.execute(
        """INSERT INTO khata
        (customer_id, amount, type, created_at)
        VALUES (?, ?, ?, ?)""",
        (customer[0], amount, "payment", datetime.now().isoformat())
    )

    conn.commit()
    conn.close()

    return f"₹{amount:.2f} payment recorded for {customer_name}."


def get_balance(customer_name):
    conn = get_connection()

    customer = conn.execute(
        "SELECT id, name FROM customers WHERE name LIKE ?",
        (f"%{customer_name}%",)
    ).fetchone()

    if not customer:
        conn.close()
        return "Customer not found."

    balance = conn.execute(
        """SELECT
           COALESCE(SUM(
               CASE
                   WHEN type = 'credit' THEN amount
                   WHEN type = 'payment' THEN -amount
                   ELSE 0
               END
           ), 0)
           FROM khata
           WHERE customer_id = ?""",
        (customer[0],)
    ).fetchone()[0]

    conn.close()

    return f"{customer[1]} owes ₹{balance:.2f}."