import streamlit as st
import sys
from pathlib import Path

# --------------------------------------------------
# Project path
# --------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.database import get_connection
from src.agent import run_agent
from src.tools.billing import create_bill
from src.tools.products import receive_stock, low_stock
from src.tools.customers import (
    add_customer,
    add_credit,
    add_payment,
    get_balance
)
from src.tools.bill_history import get_bill_history


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Nebula Supermarket",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# Dashboard statistics
# --------------------------------------------------

def get_dashboard_stats():
    conn = get_connection()

    try:
        products = conn.execute(
            "SELECT COUNT(*) FROM products"
        ).fetchone()[0]

        bills = conn.execute(
            "SELECT COUNT(*) FROM bills"
        ).fetchone()[0]

        customers = conn.execute(
            "SELECT COUNT(*) FROM customers"
        ).fetchone()[0]

        low_stock = conn.execute(
            "SELECT COUNT(*) FROM products WHERE quantity <= 10"
        ).fetchone()[0]

        return products, bills, customers, low_stock

    finally:
        conn.close()


# --------------------------------------------------
# Custom styling
# --------------------------------------------------

st.markdown(
    """
    <style>
        .main-title {
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 5px;
        }

        .subtitle {
            color: #666;
            font-size: 16px;
            margin-bottom: 25px;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

st.sidebar.title("🛒 Nebula Supermarket")
st.sidebar.caption("AI-Powered Operations Agent")

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "🧾 Billing",
        "📦 Inventory",
        "👥 Customers",
        "💳 Payments & Credit",
        "📜 Bill History",
        "🤖 AI Assistant"
    ]
)

st.sidebar.divider()
st.sidebar.caption("Nebula Supermarket Ops Agent")
st.sidebar.caption("Powered by Gemini + SQLite")


# ==================================================
# DASHBOARD
# ==================================================

if page == "🏠 Dashboard":

    st.markdown(
        '<div class="main-title">Nebula Supermarket</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'AI-powered supermarket operations dashboard'
        '</div>',
        unsafe_allow_html=True
    )

    products, bills, customers, low_stock = get_dashboard_stats()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📦 Products", products)

    with col2:
        st.metric("🧾 Bills", bills)

    with col3:
        st.metric("👥 Customers", customers)

    with col4:
        st.metric("⚠️ Low Stock", low_stock)

    st.divider()

    st.subheader("Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🧾 Create Bill", use_container_width=True):
            st.info("Select Billing from the sidebar.")

    with col2:
        if st.button("📦 Check Inventory", use_container_width=True):
            st.info("Select Inventory from the sidebar.")

    with col3:
        if st.button("🤖 Ask AI Agent", use_container_width=True):
            st.info("Select AI Assistant from the sidebar.")

    st.divider()

    st.subheader("System Status")

    st.success("🟢 Database connected")
    st.success("🟢 AI Agent available")
    st.success("🟢 Tools loaded")


# ==================================================
# BILLING
# ==================================================

elif page == "🧾 Billing":

    st.title("🧾 Create Bill")

    st.write("Create a supermarket bill using SKU and quantity.")

    col1, col2 = st.columns(2)

    with col1:
        sku = st.text_input(
            "Product SKU",
            placeholder="Example: MAGGI70"
        )

    with col2:
        quantity = st.number_input(
            "Quantity",
            min_value=1,
            value=1,
            step=1
        )

    payment_mode = st.selectbox(
        "Payment Mode",
        ["cash", "upi", "card", "credit"]
    )

    if st.button("🧾 Create Bill", type="primary"):

        if not sku.strip():
            st.warning("Please enter a product SKU.")

        else:
            try:
                result = create_bill(
                    [
                        {
                            "sku": sku.strip(),
                            "quantity": int(quantity)
                        }
                    ],
                    payment_mode
                )

                st.success("Bill created successfully!")

                st.subheader("Bill Result")
                st.write(result)

            except Exception as e:
                st.error(f"Unable to create bill: {e}")


# ==================================================
# INVENTORY
# ==================================================

elif page == "📦 Inventory":

    st.title("📦 Inventory Management")

    # ----------------------------------------------
    # Receive Stock
    # ----------------------------------------------

    st.subheader("📥 Receive Stock")

    col1, col2 = st.columns(2)

    with col1:
        product_name = st.text_input(
            "Product Name",
            placeholder="Example: Maggi 70g"
        )

    with col2:
        received_quantity = st.number_input(
            "Quantity Received",
            min_value=1,
            value=1,
            step=1
        )

    if st.button("📥 Add Stock", type="primary"):

        if not product_name.strip():
            st.warning("Please enter a product name.")

        else:
            try:
                result = receive_stock(
                    product_name.strip(),
                    int(received_quantity)
                )

                st.success("Stock received successfully!")
                st.write(result)

            except Exception as e:
                st.error(f"Unable to receive stock: {e}")

    st.divider()

    # ----------------------------------------------
    # Low Stock
    # ----------------------------------------------

    st.subheader("⚠️ Low Stock Products")

    if st.button("🔍 Check Low Stock"):

        try:
            result = low_stock()

            st.write(result)

        except Exception as e:
            st.error(f"Unable to check low stock: {e}")


# ==================================================
# CUSTOMERS
# ==================================================

# ==================================================
# CUSTOMERS
# ==================================================

elif page == "👥 Customers":

    st.title("👥 Customer Management")

    st.subheader("➕ Add Customer")

    customer_name = st.text_input(
        "Customer Name",
        placeholder="Example: Vijay"
    )

    customer_phone = st.text_input(
        "Phone Number",
        placeholder="Example: 9876543210"
    )

    if st.button("➕ Add Customer", type="primary"):

        if not customer_name.strip():
            st.warning("Please enter the customer name.")

        else:
            try:
                result = add_customer(
                    customer_name.strip(),
                    customer_phone.strip() or None
                )

                st.success("Customer added successfully!")
                st.write(result)

            except Exception as e:
                st.error(f"Unable to add customer: {e}")

    st.divider()

    st.subheader("💰 Customer Balance")

    balance_name = st.text_input(
        "Customer Name",
        placeholder="Enter customer name",
        key="balance_customer"
    )

    if st.button("🔍 Check Balance"):

        if not balance_name.strip():
            st.warning("Please enter a customer name.")

        else:
            try:
                result = get_balance(
                    balance_name.strip()
                )

                st.info(result)

            except Exception as e:
                st.error(f"Unable to get balance: {e}")


# ==================================================
# PAYMENTS
# ==================================================

# ==================================================
# PAYMENTS & CREDIT
# ==================================================

elif page == "💳 Payments & Credit":

    st.title("💳 Payments & Credit")

    # ----------------------------------------------
    # Add Credit
    # ----------------------------------------------

    st.subheader("📕 Add Khata Credit")

    credit_customer = st.text_input(
        "Customer Name",
        placeholder="Example: Vijay",
        key="credit_customer"
    )

    credit_amount = st.number_input(
        "Credit Amount (₹)",
        min_value=1.0,
        value=100.0,
        step=10.0,
        key="credit_amount"
    )

    if st.button("📕 Add Credit", type="primary"):

        if not credit_customer.strip():
            st.warning("Please enter the customer name.")

        else:
            try:
                result = add_credit(
                    credit_customer.strip(),
                    credit_amount
                )

                st.success("Credit added successfully!")
                st.write(result)

            except Exception as e:
                st.error(f"Unable to add credit: {e}")

    st.divider()

    # ----------------------------------------------
    # Add Payment
    # ----------------------------------------------

    st.subheader("💵 Record Payment")

    payment_customer = st.text_input(
        "Customer Name",
        placeholder="Example: Vijay",
        key="payment_customer"
    )

    payment_amount = st.number_input(
        "Payment Amount (₹)",
        min_value=1.0,
        value=100.0,
        step=10.0,
        key="payment_amount"
    )

    if st.button("💵 Record Payment"):

        if not payment_customer.strip():
            st.warning("Please enter the customer name.")

        else:
            try:
                result = add_payment(
                    payment_customer.strip(),
                    payment_amount
                )

                st.success("Payment recorded successfully!")
                st.write(result)

            except Exception as e:
                st.error(f"Unable to record payment: {e}")  

# ==================================================
# BILL HISTORY
# ==================================================

# ==================================================
# BILL HISTORY
# ==================================================

elif page == "📜 Bill History":

    st.title("📜 Bill History")

    st.write("View previously generated supermarket bills.")

    if st.button("🔄 Load Bill History", type="primary"):

        try:
            result = get_bill_history()

            st.subheader("Previous Bills")

            if result:
                st.write(result)
            else:
                st.info("No bills found.")

        except Exception as e:
            st.error(f"Unable to load bill history: {e}")

# ==================================================
# AI ASSISTANT
# ==================================================

elif page == "🤖 AI Assistant":

    st.title("🤖 AI Supermarket Assistant")

    st.write(
        "Ask the supermarket agent to perform "
        "an operation using natural language."
    )

    user_message = st.text_area(
        "Your request",
        placeholder=(
            "Example: Create a bill for 2 Maggi 70g "
            "packets and pay by cash."
        ),
        height=120
    )

    if st.button("🚀 Send to AI Agent", type="primary"):

        if not user_message.strip():

            st.warning("Please enter a request.")

        else:

            with st.spinner("AI Agent is processing..."):

                try:
                    response = run_agent(user_message)

                    st.success("Agent completed the request.")

                    st.subheader("Agent Response")

                    st.write(response)

                except Exception as e:

                    error_message = str(e)

                    if "quota" in error_message.lower() or "429" in error_message:

                        st.error(
                            "Gemini API quota exceeded. "
                            "Please try again later."
                        )

                    else:

                        st.error(
                            f"Agent error: {error_message}"
                        )