from src.database import get_connection
from datetime import datetime


def create_bill(items, payment_mode="cash"):
    conn = get_connection()

    try:
        total = 0
        bill_items = []

        for item in items:
            product = conn.execute(
                "SELECT id, name, price, gst_rate, quantity FROM products WHERE sku = ?",
                (item["sku"],)
            ).fetchone()

            if not product:
                return f"Product not found: {item['sku']}"

            product_id, name, price, gst_rate, stock = product
            quantity = item["quantity"]

            if quantity <= 0:
                return "Quantity must be greater than zero."

            if quantity > stock:
                return f"Insufficient stock for {name}. Available: {stock}"

            subtotal = price * quantity
            gst_amount = subtotal * gst_rate / 100
            line_total = subtotal + gst_amount

            total += line_total

            bill_items.append(
                (
                    product_id,
                    quantity,
                    price,
                    gst_rate,
                    gst_amount,
                    line_total
                )
            )

        cursor = conn.execute(
            """INSERT INTO bills
            (total, payment_mode, created_at)
            VALUES (?, ?, ?)""",
            (total, payment_mode, datetime.now().isoformat())
        )

        bill_id = cursor.lastrowid

        for product_id, quantity, price, gst_rate, gst_amount, line_total in bill_items:

            conn.execute(
                """INSERT INTO bill_items
                (bill_id, product_id, quantity, unit_price,
                 gst_rate, gst_amount, line_total)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    bill_id,
                    product_id,
                    quantity,
                    price,
                    gst_rate,
                    gst_amount,
                    line_total
                )
            )

            conn.execute(
                """UPDATE products
                SET quantity = quantity - ?
                WHERE id = ?""",
                (quantity, product_id)
            )

        conn.commit()

        return f"Bill #{bill_id} created successfully. Total: ₹{total:.2f}"

    except Exception as e:
        conn.rollback()
        return f"Billing failed: {e}"

    finally:
        conn.close()