import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

import streamlit as st

try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.database import get_connection
from src.agent import run_agent
from src.tools.billing import create_bill
from src.tools.products import receive_stock, low_stock as tool_low_stock
from src.tools.customers import add_customer, add_credit, add_payment, get_balance
from src.tools.bill_history import get_bill_history


st.set_page_config(
    page_title="Nebula Supermarket | Operations",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# GLOBAL STYLE
# =========================================================
st.markdown("""
<style>
:root{
    --bg:#0B0F14;
    --surface:#111722;
    --card:#171E2A;
    --border:rgba(255,255,255,.08);
    --accent:#5B8DEF;
    --accent-soft:rgba(91,141,239,.14);
    --success:#22C55E;
    --warning:#F59E0B;
    --danger:#EF4444;
    --text:#E7ECF3;
    --muted:#8A93A3;
}
.stApp{
    background:radial-gradient(circle at top left,#111A27 0%,var(--bg) 48%);
    color:var(--text);
}
section[data-testid="stSidebar"]{
    background:var(--surface);
    border-right:1px solid var(--border);
}
section[data-testid="stSidebar"] *{color:var(--text)!important}
h1,h2,h3,h4,p,span,label{color:var(--text)}
@keyframes fadeSlide{
    from{opacity:0;transform:translateY(9px)}
    to{opacity:1;transform:translateY(0)}
}
@keyframes pulse{
    0%,100%{opacity:.55}
    50%{opacity:1}
}
.fade{animation:fadeSlide .4s ease both}
.hero{
    background:linear-gradient(135deg,#182130,#10151F);
    border:1px solid var(--border);
    border-radius:18px;
    padding:27px 30px;
    margin-bottom:20px;
    animation:fadeSlide .45s ease both;
}
.hero-badge{
    display:inline-block;
    color:var(--accent);
    background:var(--accent-soft);
    border:1px solid rgba(91,141,239,.3);
    padding:4px 11px;
    border-radius:999px;
    font-size:10px;
    font-weight:800;
    letter-spacing:1.4px;
}
.hero-title{font-size:28px;font-weight:800;margin:9px 0 5px}
.hero-subtitle{font-size:14px;color:var(--muted);line-height:1.5}
.section{margin:20px 0 12px}
.section-title{font-size:22px;font-weight:800}
.section-subtitle{font-size:13px;color:var(--muted)}
.kpi-grid{
    display:grid;
    grid-template-columns:repeat(6,minmax(145px,1fr));
    gap:12px;
    margin-bottom:22px;
}
.kpi{
    background:var(--card);
    border:1px solid var(--border);
    border-radius:15px;
    padding:17px;
    transition:.2s;
    animation:fadeSlide .45s ease both;
}
.kpi:hover{
    transform:translateY(-3px);
    border-color:rgba(91,141,239,.42);
    box-shadow:0 12px 25px rgba(0,0,0,.25);
}
.kpi-icon{
    width:32px;height:32px;border-radius:9px;
    background:var(--accent-soft);
    display:flex;align-items:center;justify-content:center;
}
.kpi-label{
    color:var(--muted);
    font-size:10.5px;
    font-weight:800;
    letter-spacing:.55px;
    text-transform:uppercase;
    margin-top:11px;
}
.kpi-value{font-size:25px;font-weight:800;margin-top:2px}
.kpi-desc{font-size:11.5px;color:var(--muted);margin-top:3px}
.card{
    background:var(--card);
    border:1px solid var(--border);
    border-radius:15px;
    padding:18px;
    margin-bottom:12px;
    animation:fadeSlide .4s ease both;
}
.alert{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:10px;
    padding:12px 14px;
    border:1px solid var(--border);
    border-radius:12px;
    background:#141A24;
    margin-bottom:8px;
}
.badge{
    display:inline-flex;
    padding:4px 9px;
    border-radius:999px;
    font-size:10.5px;
    font-weight:800;
}
.critical{color:var(--danger);background:rgba(239,68,68,.12);border:1px solid rgba(239,68,68,.25)}
.low{color:var(--warning);background:rgba(245,158,11,.12);border:1px solid rgba(245,158,11,.25)}
.healthy{color:var(--success);background:rgba(34,197,94,.12);border:1px solid rgba(34,197,94,.25)}
.activity{
    display:flex;
    gap:12px;
    padding:10px 2px;
    border-bottom:1px dashed var(--border);
}
.activity:last-child{border-bottom:0}
.dot{
    width:9px;height:9px;border-radius:50%;
    background:var(--accent);
    margin-top:5px;
    box-shadow:0 0 7px var(--accent);
}
.activity-time{min-width:72px;color:var(--muted);font-size:11px}
.activity-title{font-size:13px;font-weight:750}
.activity-desc{font-size:11.5px;color:var(--muted)}
.activity-total{margin-left:auto;color:var(--accent);font-weight:800;font-size:13px}
.ai-row{
    display:flex;justify-content:space-between;align-items:center;
    padding:9px 0;border-bottom:1px solid var(--border);
    font-size:12.5px;
}
.ai-row:last-child{border-bottom:0}
.ai-label{color:var(--muted);font-weight:650}
.pill{
    display:inline-flex;align-items:center;gap:5px;
    border-radius:999px;padding:4px 9px;font-size:11px;font-weight:700;
}
.pill-dot{width:6px;height:6px;border-radius:50%}
.pill-ok{color:var(--success);background:rgba(34,197,94,.1)}
.pill-ok .pill-dot{background:var(--success);box-shadow:0 0 6px var(--success)}
.pill-warn{color:var(--warning);background:rgba(245,158,11,.1)}
.pill-warn .pill-dot{background:var(--warning)}
.pill-bad{color:var(--danger);background:rgba(239,68,68,.1)}
.pill-bad .pill-dot{background:var(--danger)}
.exec{
    border:1px solid var(--border);
    border-left:3px solid var(--accent);
    background:var(--card);
    border-radius:11px;
    padding:12px 15px;
    margin-bottom:6px;
    animation:fadeSlide .35s ease both;
}
.exec.pending{opacity:.65;border-left-color:var(--muted)}
.exec.failed{border-left-color:var(--danger)}
.exec-title{font-size:13px;font-weight:750}
.exec-desc{font-size:11.5px;color:var(--muted);margin-top:2px}
.exec-arrow{text-align:center;color:var(--muted);margin:0 0 4px}
.empty{
    padding:30px 15px;
    text-align:center;
    color:var(--muted);
    border:1px dashed var(--border);
    border-radius:13px;
}
.stButton>button{
    border-radius:10px!important;
    font-weight:650!important;
    border:1px solid var(--border)!important;
    transition:.15s!important;
}
.stButton>button:hover{
    transform:translateY(-1px);
    border-color:var(--accent)!important;
}
.stButton>button[kind="primary"]{
    background:var(--accent)!important;
    border-color:var(--accent)!important;
}
.stTextInput input,.stNumberInput input,.stTextArea textarea,
div[data-baseweb="select"]>div{
    background:var(--surface)!important;
    color:var(--text)!important;
    border-color:var(--border)!important;
    border-radius:10px!important;
}
div[data-testid="stDataFrame"]{
    border:1px solid var(--border);
    border-radius:11px;
    overflow:hidden;
}
.brand{padding:5px 3px 15px}
.brand-title{font-size:20px;font-weight:850}
.brand-sub{font-size:11px;color:var(--muted)}
.nav-caption{
    color:var(--muted);
    font-size:10px;
    font-weight:800;
    letter-spacing:1.2px;
    text-transform:uppercase;
    margin:13px 0 6px;
}
@media(max-width:1100px){
    .kpi-grid{grid-template-columns:repeat(3,1fr)}
}
@media(max-width:700px){
    .kpi-grid{grid-template-columns:repeat(2,1fr)}
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# HELPERS
# =========================================================
def inr(value):
    try:
        return f"₹{float(value):,.2f}"
    except (TypeError, ValueError):
        return "₹0.00"


def hero(badge, title, subtitle):
    st.markdown(
        f'<div class="hero"><div class="hero-badge">{badge}</div>'
        f'<div class="hero-title">{title}</div>'
        f'<div class="hero-subtitle">{subtitle}</div></div>',
        unsafe_allow_html=True,
    )


def section_header(badge, title, subtitle):
    st.markdown(
        f'<div class="section"><div class="nav-caption">{badge}</div>'
        f'<div class="section-title">{title}</div>'
        f'<div class="section-subtitle">{subtitle}</div></div>',
        unsafe_allow_html=True,
    )


def pill(text, level="ok"):
    cls = {"ok":"pill-ok","warn":"pill-warn","bad":"pill-bad"}.get(level,"pill-ok")
    return f'<span class="pill {cls}"><span class="pill-dot"></span>{text}</span>'


def alert_badge(status):
    cls = {"CRITICAL":"critical","LOW":"low","HEALTHY":"healthy"}.get(status,"healthy")
    icon = {"CRITICAL":"🔴","LOW":"🟡","HEALTHY":"🟢"}.get(status,"🟢")
    return f'<span class="badge {cls}">{icon} {status}</span>'


def empty_state(message):
    st.markdown(f'<div class="empty">{message}</div>', unsafe_allow_html=True)


def relative_time(value):
    if not value:
        return "—"
    raw = str(value)
    parsed = None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S.%f"):
        try:
            parsed = datetime.strptime(raw[:26] if "%f" in fmt else raw[:19], fmt)
            break
        except ValueError:
            pass
    if not parsed:
        return raw
    seconds = int((datetime.now() - parsed).total_seconds())
    if seconds < 0:
        return raw
    if seconds < 60:
        return "just now"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} min ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} hr ago"
    days = hours // 24
    return f"{days} day{'s' if days != 1 else ''} ago"


def show_error(prefix, exc):
    print(f"[ERROR] {prefix}: {exc}")
    st.error(f"{prefix}. Please try again.")
    with st.expander("Technical details"):
        st.code(str(exc))


def goto(label):
    st.session_state.nav_page = label
    st.rerun()


# =========================================================
# DATABASE READ HELPERS
# =========================================================
def db_all_products():
    conn = get_connection()
    try:
        return conn.execute(
            """SELECT id,name,sku,price,quantity,reorder_level
               FROM products ORDER BY name"""
        ).fetchall()
    finally:
        conn.close()


def db_all_customers():
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT id,name,phone FROM customers ORDER BY name"
        ).fetchall()
    except Exception:
        return []
    finally:
        conn.close()


def db_kpi_stats():
    conn = get_connection()
    try:
        products = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        todays_bills = conn.execute(
            "SELECT COUNT(*) FROM bills "
            "WHERE date(created_at)=date('now','localtime')"
        ).fetchone()[0]
        todays_revenue = conn.execute(
            "SELECT COALESCE(SUM(total),0) FROM bills "
            "WHERE date(created_at)=date('now','localtime')"
        ).fetchone()[0]
        try:
            customers = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
        except Exception:
            customers = 0
        low_stock = conn.execute(
            "SELECT COUNT(*) FROM products WHERE quantity <= reorder_level"
        ).fetchone()[0]
        outstanding = 0.0
        try:
            rows = conn.execute("""
                SELECT customer_id,
                       SUM(CASE
                           WHEN lower(type)='credit' THEN amount
                           WHEN lower(type)='payment' THEN -amount
                           ELSE 0
                       END)
                FROM khata
                GROUP BY customer_id
            """).fetchall()
            outstanding = sum(v for _, v in rows if v and v > 0)
        except Exception:
            pass
        return {
            "products": products,
            "todays_bills": todays_bills,
            "todays_revenue": todays_revenue,
            "customers": customers,
            "low_stock": low_stock,
            "outstanding_credit": outstanding,
        }
    finally:
        conn.close()


def db_revenue_trend(days=7):
    conn = get_connection()
    try:
        rows = conn.execute(
            f"""SELECT date(created_at),COALESCE(SUM(total),0),COUNT(*)
                FROM bills
                WHERE date(created_at)>=date('now','localtime','-{days-1} days')
                GROUP BY date(created_at)
                ORDER BY date(created_at)"""
        ).fetchall()
    finally:
        conn.close()

    by_date = {d: (rev, count) for d, rev, count in rows}
    today = datetime.now().date()
    result = []
    for i in range(days - 1, -1, -1):
        d = (today - timedelta(days=i)).isoformat()
        rev, count = by_date.get(d, (0, 0))
        result.append({"date": d, "revenue": rev, "bills": count})
    return result


def db_top_products(limit=5):
    conn = get_connection()
    try:
        return conn.execute(
            """SELECT p.name,SUM(bi.quantity),SUM(bi.line_total)
               FROM bill_items bi
               JOIN products p ON bi.product_id=p.id
               GROUP BY p.id
               ORDER BY SUM(bi.quantity) DESC
               LIMIT ?""",
            (limit,),
        ).fetchall()
    except Exception:
        return []
    finally:
        conn.close()


def db_inventory_alerts():
    alerts = []
    for _id, name, sku, price, qty, reorder in db_all_products():
        if qty == 0:
            status = "CRITICAL"
        elif qty <= reorder:
            status = "LOW"
        else:
            status = "HEALTHY"
        alerts.append({
            "name": name, "sku": sku, "qty": qty,
            "reorder": reorder, "status": status
        })
    order = {"CRITICAL":0, "LOW":1, "HEALTHY":2}
    alerts.sort(key=lambda x: order[x["status"]])
    return alerts


def db_recent_bills(limit=6):
    conn = get_connection()
    try:
        return conn.execute(
            """SELECT id,total,payment_mode,created_at
               FROM bills ORDER BY id DESC LIMIT ?""",
            (limit,),
        ).fetchall()
    finally:
        conn.close()


def db_bill_history_structured():
    conn = get_connection()
    try:
        bills = conn.execute(
            """SELECT b.id,c.name,b.total,b.payment_mode,b.created_at
               FROM bills b
               LEFT JOIN customers c ON b.customer_id=c.id
               ORDER BY b.id DESC"""
        ).fetchall()
        result = []
        for bill_id, customer, total, mode, created_at in bills:
            items = conn.execute(
                """SELECT p.name,bi.quantity,bi.unit_price,bi.line_total
                   FROM bill_items bi
                   JOIN products p ON bi.product_id=p.id
                   WHERE bi.bill_id=?""",
                (bill_id,),
            ).fetchall()
            result.append({
                "id": bill_id,
                "customer": customer or "Walk-in customer",
                "total": total,
                "payment_mode": mode,
                "created_at": created_at,
                "items": items,
            })
        return result
    except Exception:
        return []
    finally:
        conn.close()


# =========================================================
# NAVIGATION
# =========================================================
NAV_ITEMS = [
    "🏠 Command Center",
    "🧾 Billing",
    "📦 Inventory",
    "👥 Customers",
    "💳 Payments & Credit",
    "📜 Bill History",
    "🤖 AI Assistant",
]

if "nav_page" not in st.session_state:
    st.session_state.nav_page = NAV_ITEMS[0]
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "ai_last_request" not in st.session_state:
    st.session_state.ai_last_request = "—"
if "ai_last_operation" not in st.session_state:
    st.session_state.ai_last_operation = "—"
if "ai_last_status" not in st.session_state:
    st.session_state.ai_last_status = "IDLE"
if "ai_trace" not in st.session_state:
    st.session_state.ai_trace = []

with st.sidebar:
    st.markdown(
        '<div class="brand"><div class="brand-title">🛒 NEBULA</div>'
        '<div class="brand-sub">Intelligent Operations</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="nav-caption">Operations</div>', unsafe_allow_html=True)

    selected = st.radio(
        "Navigation",
        NAV_ITEMS,
        index=NAV_ITEMS.index(st.session_state.nav_page),
        key="nav_radio",
        label_visibility="collapsed",
    )
    if selected != st.session_state.nav_page:
        st.session_state.nav_page = selected

    st.markdown('<div class="nav-caption">System</div>', unsafe_allow_html=True)

    try:
        conn = get_connection()
        conn.close()
        st.markdown(pill("Database Online", "ok"), unsafe_allow_html=True)
    except Exception:
        st.markdown(pill("Database Offline", "bad"), unsafe_allow_html=True)

    if os.getenv("GEMINI_API_KEY"):
        st.markdown(pill("Gemini Configured", "ok"), unsafe_allow_html=True)
    else:
        st.markdown(pill("Gemini Key Missing", "warn"), unsafe_allow_html=True)

    st.divider()
    st.caption("Nebula Supermarket Ops Agent")
    st.caption("Streamlit · SQLite · Gemini")

page = st.session_state.nav_page.split(" ", 1)[1]


# =========================================================
# COMMAND CENTER
# =========================================================
if page == "Command Center":
    hero(
        "COMMAND CENTER",
        "Nebula Supermarket — Operations Command Center",
        "Monitor sales, inventory, customers and AI-powered supermarket "
        "operations from one place.",
    )

    try:
        kpi = db_kpi_stats()
    except Exception as e:
        show_error("Could not load dashboard statistics", e)
        kpi = dict(products=0, todays_bills=0, todays_revenue=0,
                   customers=0, low_stock=0, outstanding_credit=0)

    cards = [
        ("📦","Total Products",kpi["products"],"products in inventory"),
        ("🧾","Today's Bills",kpi["todays_bills"],"bills created today"),
        ("💰","Today's Revenue",inr(kpi["todays_revenue"]),"today's sales"),
        ("👥","Total Customers",kpi["customers"],"registered customers"),
        ("⚠️","Low Stock Items",kpi["low_stock"],"at or below reorder level"),
        ("📕","Outstanding Credit",inr(kpi["outstanding_credit"]),"positive Khata balance"),
    ]
    html = '<div class="kpi-grid">'
    for icon, label, value, desc in cards:
        html += (
            f'<div class="kpi"><div class="kpi-icon">{icon}</div>'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value}</div>'
            f'<div class="kpi-desc">{desc}</div></div>'
        )
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

    st.markdown("### 📈 Sales & Revenue Analytics")
    try:
        trend = db_revenue_trend(7)
    except Exception as e:
        show_error("Could not load revenue analytics", e)
        trend = []

    revenue_7d = sum(x["revenue"] for x in trend)
    bills_7d = sum(x["bills"] for x in trend)

    a, b, c = st.columns(3)
    a.metric("Revenue Today", inr(kpi["todays_revenue"]))
    b.metric("Revenue · 7 Days", inr(revenue_7d))
    c.metric("Bills · 7 Days", bills_7d)

    if bills_7d == 0:
        empty_state("No sales recorded yet. Create your first bill to populate analytics.")
    else:
        dates = [x["date"] for x in trend]
        revenues = [x["revenue"] for x in trend]
        bill_counts = [x["bills"] for x in trend]
        if PLOTLY_AVAILABLE:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates, y=revenues, mode="lines+markers",
                name="Revenue (₹)",
                line=dict(color="#5B8DEF", width=3),
                marker=dict(size=7),
                fill="tozeroy",
                fillcolor="rgba(91,141,239,.12)",
            ))
            fig.add_trace(go.Bar(
                x=dates, y=bill_counts, name="Bills",
                yaxis="y2", opacity=.38,
            ))
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=330,
                margin=dict(l=10,r=10,t=10,b=10),
                yaxis=dict(title="Revenue (₹)", gridcolor="rgba(255,255,255,.06)"),
                yaxis2=dict(title="Bills", overlaying="y", side="right", showgrid=False),
                xaxis=dict(gridcolor="rgba(255,255,255,.06)"),
                legend=dict(orientation="h"),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.line_chart({"Revenue (₹)": revenues})
            st.bar_chart({"Bills": bill_counts})

    left, right = st.columns([1.2, 1])

    with left:
        st.markdown("### 🏆 Top-Selling Products")
        top = db_top_products(5)
        if not top:
            empty_state("No sales yet — top products will appear after bills are created.")
        else:
            for rank, (name, qty, revenue) in enumerate(top, 1):
                st.markdown(
                    f'<div class="card"><b>#{rank} · {name}</b>'
                    f'<div style="color:var(--muted);font-size:12px">'
                    f'{int(qty)} units sold</div>'
                    f'<div style="color:var(--accent);font-weight:800;margin-top:4px">'
                    f'{inr(revenue)}</div></div>',
                    unsafe_allow_html=True,
                )

        st.markdown("### 🕒 Recent Activity")
        recent = db_recent_bills(6)
        if not recent:
            empty_state("No activity yet — create your first bill.")
        else:
            rows = '<div class="card">'
            for bill_id, total, mode, created_at in recent:
                rows += (
                    f'<div class="activity"><div class="activity-time">'
                    f'{relative_time(created_at)}</div><div class="dot"></div>'
                    f'<div><div class="activity-title">Bill Created</div>'
                    f'<div class="activity-desc">Bill #{bill_id} · {str(mode).upper()}</div>'
                    f'</div><div class="activity-total">{inr(total)}</div></div>'
                )
            rows += "</div>"
            st.markdown(rows, unsafe_allow_html=True)

    with right:
        st.markdown("### ⚠️ Inventory Alerts")
        alerts = db_inventory_alerts()
        if not alerts:
            empty_state("No products in inventory.")
        else:
            urgent = [x for x in alerts if x["status"] != "HEALTHY"]
            display = (urgent or alerts)[:6]
            for item in display:
                st.markdown(
                    f'<div class="alert"><div><b>{item["name"]}</b>'
                    f'<div style="color:var(--muted);font-size:11.5px">'
                    f'{item["sku"]} · {item["qty"]} in stock · reorder at '
                    f'{item["reorder"]}</div></div>'
                    f'{alert_badge(item["status"])}</div>',
                    unsafe_allow_html=True,
                )
            if not urgent:
                st.caption("✅ All products are healthily stocked.")
            if st.button("📦 View Inventory", use_container_width=True):
                goto("📦 Inventory")

        st.markdown("### 🤖 AI Operations")
        gemini_ok = bool(os.getenv("GEMINI_API_KEY"))
        last_status = st.session_state.ai_last_status
        level = {"SUCCESS":"ok","FAILED":"bad","IDLE":"warn"}.get(last_status,"warn")
        tools_count = 8
        st.markdown(
            '<div class="card">'
            f'<div class="ai-row"><span class="ai-label">AI Agent</span>{pill("Online" if gemini_ok else "Offline","ok" if gemini_ok else "bad")}</div>'
            f'<div class="ai-row"><span class="ai-label">Gemini</span>{pill("Configured" if gemini_ok else "Not Configured","ok" if gemini_ok else "warn")}</div>'
            f'<div class="ai-row"><span class="ai-label">Tools</span>{pill(f"{tools_count} tools loaded","ok")}</div>'
            f'<div class="ai-row"><span class="ai-label">Database</span>{pill("Connected","ok")}</div>'
            f'<div class="ai-row"><span class="ai-label">Last Request</span><span style="color:var(--muted);max-width:55%;text-align:right">{st.session_state.ai_last_request}</span></div>'
            f'<div class="ai-row"><span class="ai-label">Last Operation</span><span style="color:var(--muted)">{st.session_state.ai_last_operation}</span></div>'
            f'<div class="ai-row"><span class="ai-label">Last Status</span>{pill(last_status,level)}</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    st.markdown("### ⚡ Quick Actions")
    q1,q2,q3,q4 = st.columns(4)
    if q1.button("🧾 Create Bill", use_container_width=True):
        goto("🧾 Billing")
    if q2.button("📦 Check Inventory", use_container_width=True):
        goto("📦 Inventory")
    if q3.button("🤖 Ask AI Agent", use_container_width=True):
        goto("🤖 AI Assistant")
    if q4.button("📜 View Bill History", use_container_width=True):
        goto("📜 Bill History")


# =========================================================
# BILLING
# =========================================================
elif page == "Billing":
    section_header(
        "BILLING TERMINAL",
        "Sales & Billing",
        "Process transactions with stock validation and GST calculation.",
    )
    products = db_all_products()
    if not products:
        st.warning("No products found. Add products to the database first.")
    else:
        options = {
            f"{name} · {sku} · {inr(price)} · {qty} in stock":
            (sku,name,price,qty)
            for _id,name,sku,price,qty,reorder in products
        }
        c1,c2 = st.columns([2,1])
        selected = c1.selectbox("Product", list(options))
        sku,name,unit_price,available = options[selected]
        quantity = c2.number_input("Quantity", min_value=1, value=1, step=1)
        mode = st.selectbox("Payment Mode", ["cash","upi","card","credit"])
        customer = None
        if mode == "credit":
            customer = st.text_input(
                "Customer Name",
                placeholder="Required for credit sales",
            )
        st.markdown("#### Bill Preview")
        x1,x2,x3 = st.columns(3)
        x1.metric("Unit Price",inr(unit_price))
        x2.metric("Quantity",int(quantity))
        x3.metric("Subtotal",inr(unit_price*quantity))
        if quantity > available:
            st.error(f"Insufficient stock: requested {quantity}, available {available}.")
        if st.button("🧾 Create Bill", type="primary"):
            if mode == "credit" and not customer.strip():
                st.warning("Please enter a customer name for credit sales.")
            else:
                try:
                    result = create_bill(
                        [{"sku":sku,"quantity":int(quantity)}],
                        mode,
                        customer.strip() if customer else None,
                    )
                    if str(result).lower().startswith("bill #"):
                        st.success(result)
                        st.session_state.ai_last_operation = "Bill created"
                        st.session_state.ai_last_status = "SUCCESS"
                        st.rerun()
                    else:
                        st.warning(result)
                except Exception as e:
                    show_error("Unable to create bill",e)


# =========================================================
# INVENTORY
# =========================================================
elif page == "Inventory":
    section_header(
        "INVENTORY CONTROL",
        "Inventory Management",
        "Monitor stock levels and receive incoming inventory.",
    )
    products = db_all_products()
    search = st.text_input("🔍 Search products", placeholder="Search by name or SKU")
    filtered = [
        p for p in products
        if not search or search.lower() in p[1].lower() or search.lower() in p[2].lower()
    ]
    if filtered:
        rows = []
        for _id,name,sku,price,qty,reorder in filtered:
            status = "🔴 Reorder" if qty <= reorder else "🟢 Healthy"
            rows.append({
                "Product":name,"SKU":sku,"Price":inr(price),
                "Stock":qty,"Reorder Level":reorder,"Status":status
            })
        st.dataframe(rows,use_container_width=True,hide_index=True)
    else:
        empty_state("No matching products found.")

    st.divider()
    left,right = st.columns(2)
    with left:
        st.markdown("### 📥 Receive Stock")
        product_name = st.text_input("Product Name",placeholder="Example: Maggi 70g")
        received = st.number_input("Quantity Received",min_value=1,value=1,step=1)
        if st.button("📥 Add Stock",type="primary"):
            if not product_name.strip():
                st.warning("Please enter a product name.")
            else:
                try:
                    st.success(receive_stock(product_name.strip(),int(received)))
                    st.rerun()
                except Exception as e:
                    show_error("Unable to receive stock",e)
    with right:
        st.markdown("### ⚠️ Low Stock Report")
        try:
            report = tool_low_stock()
            if report == "No low-stock products.":
                st.success("All products are healthy.")
            else:
                st.code(report)
        except Exception as e:
            show_error("Unable to check low stock",e)


# =========================================================
# CUSTOMERS
# =========================================================
elif page == "Customers":
    section_header(
        "CUSTOMER MANAGEMENT",
        "Customer Accounts",
        "Manage customers and inspect their running Khata balances.",
    )
    customers = db_all_customers()
    left,right = st.columns([1.2,1])
    with left:
        st.markdown("### Directory")
        if customers:
            st.dataframe(
                [{"Name":n,"Phone":p or "—"} for _id,n,p in customers],
                use_container_width=True,hide_index=True
            )
        else:
            empty_state("No customers yet.")
        st.markdown("### 💰 Check Balance")
        names = [n for _id,n,p in customers]
        selected_name = (
            st.selectbox("Customer",names,key="customer_balance_select")
            if names else
            st.text_input("Customer Name",key="customer_balance_input")
        )
        if st.button("🔍 Check Balance"):
            try:
                st.info(get_balance(str(selected_name).strip()))
            except Exception as e:
                show_error("Unable to get balance",e)
    with right:
        st.markdown("### ➕ Add Customer")
        name = st.text_input("Customer Name",placeholder="Example: Ravi",key="new_customer_name")
        phone = st.text_input("Phone Number",placeholder="Example: 9876543210",key="new_customer_phone")
        if st.button("➕ Add Customer",type="primary"):
            if not name.strip():
                st.warning("Please enter a customer name.")
            else:
                try:
                    st.success(add_customer(name.strip(),phone.strip() or None))
                    st.rerun()
                except Exception as e:
                    show_error("Unable to add customer",e)


# =========================================================
# PAYMENTS & CREDIT
# =========================================================
elif page == "Payments & Credit":
    section_header(
        "KHATA MANAGEMENT",
        "Payments & Credit",
        "Record credit and payments against customer accounts.",
    )
    customers = db_all_customers()
    names = [n for _id,n,p in customers]
    left,right = st.columns(2)
    with left:
        st.markdown("### 📕 Add Khata Credit")
        customer = (
            st.selectbox("Customer",names,key="credit_customer")
            if names else
            st.text_input("Customer Name",key="credit_customer_text")
        )
        amount = st.number_input("Credit Amount (₹)",min_value=1.0,value=100.0,step=10.0,key="credit_amount")
        if st.button("📕 Add Credit",type="primary"):
            try:
                st.success(add_credit(str(customer).strip(),amount))
            except Exception as e:
                show_error("Unable to add credit",e)
    with right:
        st.markdown("### 💵 Record Payment")
        customer = (
            st.selectbox("Customer",names,key="payment_customer")
            if names else
            st.text_input("Customer Name",key="payment_customer_text")
        )
        amount = st.number_input("Payment Amount (₹)",min_value=1.0,value=100.0,step=10.0,key="payment_amount")
        if st.button("💵 Record Payment"):
            try:
                st.success(add_payment(str(customer).strip(),amount))
            except Exception as e:
                show_error("Unable to record payment",e)

    st.divider()
    st.markdown("### 💰 Check Balance")
    customer = (
        st.selectbox("Customer",names,key="pc_balance_customer")
        if names else
        st.text_input("Customer Name",key="pc_balance_text")
    )
    if st.button("🔍 Check Balance",key="pc_balance_button"):
        try:
            st.info(get_balance(str(customer).strip()))
        except Exception as e:
            show_error("Unable to get balance",e)


# =========================================================
# BILL HISTORY
# =========================================================
elif page == "Bill History":
    section_header(
        "TRANSACTION LOG",
        "Transaction History",
        "Browse bills recorded in the supermarket database.",
    )
    bills = db_bill_history_structured()
    if not bills:
        empty_state("No bills found yet.")
    else:
        c1,c2 = st.columns([2,1])
        search = c1.text_input("🔍 Search by customer or bill ID")
        mode = c2.selectbox("Payment Mode",["All","cash","upi","card","credit"])
        shown = 0
        for bill in bills:
            if search:
                s = search.lower()
                if s not in bill["customer"].lower() and s != str(bill["id"]):
                    continue
            if mode != "All" and str(bill["payment_mode"]).lower() != mode:
                continue
            shown += 1
            st.markdown(
                f'<div class="card"><div style="display:flex;justify-content:space-between">'
                f'<div><b>Bill #{bill["id"]} — {bill["customer"]}</b>'
                f'<div style="color:var(--muted);font-size:11.5px">'
                f'{str(bill["payment_mode"]).upper()} · {bill["created_at"]}</div></div>'
                f'<div style="color:var(--accent);font-weight:850">{inr(bill["total"])}</div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )
            with st.expander(f"View items — Bill #{bill['id']}"):
                for name,qty,price,line_total in bill["items"]:
                    st.write(f"{name} × {qty} · {inr(price)} each · {inr(line_total)}")
        if shown == 0:
            empty_state("No bills match the selected filters.")


# =========================================================
# AI ASSISTANT + FEATURE 7
# =========================================================
elif page == "AI Assistant":
    section_header(
        "AI OPERATIONS",
        "Supermarket AI Assistant",
        "Control supermarket operations using natural language.",
    )

    with st.expander("💡 Example commands", expanded=False):
        st.markdown(
            "- Check the stock of Maggi 70g\n"
            "- Create a bill for 2 Maggi 70g packets and pay by cash\n"
            "- Add customer Ravi with phone number 9876543210\n"
            "- How much does Ravi owe?\n"
            "- Add ₹500 credit to Ravi\n"
            "- Record a payment of ₹200 from Ravi\n"
            "- Show previous bills"
        )

    for role,msg in st.session_state.chat_history:
        with st.chat_message(role):
            st.write(msg)

    user_message = st.chat_input("Ask the assistant to perform an operation…")

    if user_message:
        st.session_state.chat_history.append(("user",user_message))
        st.session_state.ai_last_request = user_message
        st.session_state.ai_last_operation = "Processing request"
        st.session_state.ai_last_status = "IDLE"

        with st.chat_message("user"):
            st.write(user_message)

        with st.chat_message("assistant"):
            st.markdown("#### 🔄 AI Execution Timeline")

            st.markdown(
                f'<div class="exec"><div class="exec-title">✓ User Request</div>'
                f'<div class="exec-desc">{user_message[:160]}</div></div>',
                unsafe_allow_html=True,
            )
            st.markdown('<div class="exec-arrow">↓</div>',unsafe_allow_html=True)

            trace_placeholder = st.empty()
            trace_events = []

            def render_trace():
                blocks = []
                for i, event in enumerate(trace_events):
                    event_type = event.get("type", "")
                    if event_type == "gemini":
                        title = "✓ Gemini" if event.get("status") == "started" else "✓ Gemini Response"
                        desc = (
                            "Understanding request and selecting tools…"
                            if event.get("status") == "started"
                            else "Gemini completed the reasoning cycle."
                        )
                        state = "pending" if event.get("status") == "started" else ""
                    elif event_type == "tool" and event.get("status") == "started":
                        title = f"⚙ Tool: {event.get('name', 'unknown')}"
                        desc = f"Arguments: {str(event.get('arguments', {}))[:220]}"
                        state = "pending"
                    elif event_type == "tool" and event.get("status") == "completed":
                        title = f"✓ Tool: {event.get('name', 'unknown')}"
                        desc = f"Result: {str(event.get('result', ''))[:260]}"
                        state = ""
                    elif event_type == "tool" and event.get("status") == "failed":
                        title = f"✗ Tool: {event.get('name', 'unknown')}"
                        desc = f"Error: {str(event.get('error', 'Unknown error'))[:260]}"
                        state = "failed"
                    elif event_type == "response":
                        title = "✓ Final Response"
                        desc = "Response ready for the operator."
                        state = ""
                    else:
                        continue
                    blocks.append(
                        f'<div class="exec {state}"><div class="exec-title">{title}</div>'
                        f'<div class="exec-desc">{desc}</div></div>'
                    )
                    if i < len(trace_events) - 1:
                        blocks.append('<div class="exec-arrow">↓</div>')
                trace_placeholder.markdown("".join(blocks), unsafe_allow_html=True)

            def trace_callback(event):
                trace_events.append(event)
                render_trace()

            trace_callback({"type": "gemini", "status": "started"})

            try:
                with st.spinner("AI agent is processing the operation…"):
                    response = run_agent(user_message, trace_callback=trace_callback)

                st.write(response)
                st.session_state.chat_history.append(("assistant",response))
                st.session_state.ai_last_operation = user_message[:80]
                st.session_state.ai_last_status = "SUCCESS"

                st.write(response)
                st.session_state.chat_history.append(("assistant",response))
                st.session_state.ai_last_operation = user_message[:80]
                st.session_state.ai_last_status = "SUCCESS"

            except Exception as e:
                error = str(e)
                print(f"[ERROR] AI agent failure: {error}")
                if "quota" in error.lower() or "429" in error:
                    friendly = "AI Agent unavailable — Gemini API quota exceeded. Please try again later."
                elif "GEMINI_API_KEY" in error:
                    friendly = "AI Agent is not configured. Please set GEMINI_API_KEY."
                else:
                    friendly = "AI Agent could not complete the request. Please check the configuration and try again."

                gemini_placeholder.markdown(
                    '<div class="exec failed"><div class="exec-title">✗ Gemini</div>'
                    '<div class="exec-desc">Request failed.</div></div>',
                    unsafe_allow_html=True,
                )
                st.markdown('<div class="exec-arrow">↓</div>',unsafe_allow_html=True)
                st.markdown(
                    f'<div class="exec failed"><div class="exec-title">✗ Final Response</div>'
                    f'<div class="exec-desc">{friendly}</div></div>',
                    unsafe_allow_html=True,
                )
                st.error(friendly)
                st.session_state.chat_history.append(("assistant",friendly))
                st.session_state.ai_last_operation = user_message[:80]
                st.session_state.ai_last_status = "FAILED"
