from src.database import get_connection


def get_bill_history():
    conn = get_connection()

    rows = conn.execute(
        """
        SELECT id, total, payment_mode, created_at
        FROM bills
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()

    if not rows:
        return "No bills found."

    return "\n".join(
        f"Bill #{bill_id} | Total: ₹{total:.2f} | "
        f"Payment: {payment_mode} | {created_at}"
        for bill_id, total, payment_mode, created_at in rows
    )