from src.database import get_connection

def add_product(name, sku, cost_price, price, gst_rate, hsn_code, unit, quantity, reorder_level=5):
    conn = get_connection()

    conn.execute(
        """INSERT INTO products
        (name, sku, cost_price, price, gst_rate, hsn_code, unit, quantity, reorder_level)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (name, sku, cost_price, price, gst_rate, hsn_code, unit, quantity, reorder_level)
    )

    conn.commit()
    conn.close()

    return f"{name} added successfully." 

def check_stock(name):
    conn = get_connection()

    row = conn.execute(
        "SELECT name, sku, price, quantity FROM products WHERE name LIKE ?",
        (f"%{name}%",)
    ).fetchone()

    conn.close()

    if not row:
        return "Product not found."

    return f"{row[0]} | SKU: {row[1]} | Price: ₹{row[2]} | Stock: {row[3]}"


def receive_stock(name, quantity):
    if quantity <= 0:
        return "Quantity must be greater than zero."

    conn = get_connection()

    result = conn.execute(
        "UPDATE products SET quantity = quantity + ? WHERE name LIKE ?",
        (quantity, f"%{name}%")
    )

    conn.commit()
    conn.close()

    if result.rowcount == 0:
        return "Product not found."

    return f"Added {quantity} units of {name}."
def low_stock():
    conn = get_connection()

    rows = conn.execute(
        "SELECT name, quantity, reorder_level FROM products WHERE quantity <= reorder_level"
    ).fetchall()

    conn.close()

    if not rows:
        return "No low-stock products."

    return "\n".join(
        f"{name}: {quantity} units remaining"
        for name, quantity, reorder_level in rows
    )