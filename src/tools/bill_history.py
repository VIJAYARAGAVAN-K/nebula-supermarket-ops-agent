from src.database import get_connection


def get_bill_history():
    conn = get_connection()

    bills = conn.execute(
        """
        SELECT
            b.id,
            c.name,
            b.total,
            b.payment_mode,
            b.created_at
        FROM bills b
        LEFT JOIN customers c ON b.customer_id = c.id
        ORDER BY b.id DESC
        """
    ).fetchall()

    if not bills:
        conn.close()
        return "No bills found."

    output = []

    for bill_id, customer_name, total, payment_mode, created_at in bills:

        items = conn.execute(
            """
            SELECT
                p.name,
                bi.quantity,
                bi.unit_price,
                bi.line_total
            FROM bill_items bi
            JOIN products p ON bi.product_id = p.id
            WHERE bi.bill_id = ?
            """,
            (bill_id,)
        ).fetchall()

        customer_text = customer_name if customer_name else "Walk-in customer"

        output.append(
            f"Bill #{bill_id} | Customer: {customer_text} | "
            f"Total: ₹{total:.2f} | Payment: {payment_mode} | "
            f"Date: {created_at}"
        )

        for name, quantity, unit_price, line_total in items:
            output.append(
                f"  - {name} x {quantity} | "
                f"₹{unit_price:.2f} each | ₹{line_total:.2f}"
            )

    conn.close()

    return "\n".join(output)