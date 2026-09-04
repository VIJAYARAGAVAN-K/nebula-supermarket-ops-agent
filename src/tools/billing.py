from src.database import get_connection
from datetime import datetime


def create_bill(items, payment_mode="cash", customer_name=None):
    conn = get_connection()

    try:
        total = 0
        bill_items = []
        customer_id = None

        # Find customer if provided
        if customer_name:
            customer = conn.execute(
                "SELECT id FROM customers WHERE name LIKE ?",
                (f"%{customer_name}%",)
            ).fetchone()

            if not customer:
                return "Customer not found."

            customer_id = customer[0]

        # Validate products and calculate bill
        for item in items:
            product = conn.execute(
                """SELECT id, name, price, gst_rate, quantity
                   FROM products WHERE sku = ?""",
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

        # Credit sales require a customer
        if payment_mode.lower() == "credit" and not customer_id:
            return "Customer name is required for credit sales."

        # Create bill
        cursor = conn.execute(
            """INSERT INTO bills
            (customer_id, total, payment_mode, created_at)
            VALUES (?, ?, ?, ?)""",
            (
                customer_id,
                total,
                payment_mode,
                datetime.now().isoformat()
            )
        )

        bill_id = cursor.lastrowid

        # Add bill items and reduce stock
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

        # Add credit to Khata
        if payment_mode.lower() == "credit":
            conn.execute(
                """INSERT INTO khata
                (customer_id, amount, type, created_at)
                VALUES (?, ?, ?, ?)""",
                (
                    customer_id,
                    total,
                    "credit",
                    datetime.now().isoformat()
                )
            )

        conn.commit()

        return f"Bill #{bill_id} created successfully. Total: ₹{total:.2f}"

    except Exception as e:
        conn.rollback()
        return f"Billing failed: {e}"

    finally:
        conn.close()