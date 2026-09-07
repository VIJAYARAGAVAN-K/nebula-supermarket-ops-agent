# 🛒 Nebula Supermarket Ops Agent

> **AI-powered operations assistant for an Indian supermarket / kirana store**
>
> Built with **Python, Gemini, SQLite and Streamlit**.

## Overview

Nebula Supermarket Ops Agent is an AI-driven supermarket operations system that lets a store operator manage inventory, billing, customers and credit using natural-language instructions.

Instead of relying on a large rule-based `if/elif` intent router, the application uses **Gemini function calling** to understand a request, select the appropriate business tool, execute the operation against SQLite, receive the tool result, and continue the reasoning loop when another tool is required.

The project currently includes a professional Streamlit operations dashboard alongside the conversational AI assistant.

## Current Capabilities

### 1. Command Center KPI Dashboard

The dashboard provides a live operational snapshot:

- Total products
- Today's bills
- Today's revenue
- Total customers
- Low-stock items
- Outstanding customer credit

<img width="1917" height="790" alt="image" src="https://github.com/user-attachments/assets/3e7ec871-4569-4b3b-be8e-3c65f73a060b" />


### 2. Sales & Revenue Analytics

- Today's revenue
- Recent revenue trend
- Bills per day
- Revenue visualization
- Operational sales summary

  <img width="1917" height="892" alt="image" src="https://github.com/user-attachments/assets/dc912728-93e1-416e-8566-d3aab769372c" />


### 3. Top-Selling Products

- Top 5 products by quantity sold
- Quantity sold
- Sales revenue
- Product-level sales performance

 <img width="1915" height="970" alt="image" src="https://github.com/user-attachments/assets/6baa7f99-3fbe-4132-ba6d-c14f997255c2" />


### 4. Low-Stock Alert Center

Products are classified using their reorder level:

- 🔴 **CRITICAL** — stock is zero
- 🟠 **LOW** — stock is at or below reorder level
- 🟢 **HEALTHY** — stock is above reorder level

### 5. Recent Activity Timeline

The command center surfaces recent billing activity from the database so the operator can quickly understand what has happened in the store.

### 6. AI Operations Panel

The dashboard exposes operational AI status, including:

- Gemini agent availability
- Registered tool count
- Database availability
- Last AI request
- Last operation
- Last operation status

### 7. AI Execution Timeline

The AI Assistant now exposes the actual function-calling flow instead of displaying a generic loading animation:

```text
User Request
      ↓
Gemini
      ↓
Tool Selection
      ↓
Tool Execution
      ↓
Database / Business Result
      ↓
Gemini continues reasoning if required
      ↓
Final Response
```

The agent supports an optional `trace_callback`, while the original `run_agent(user_message)` usage remains valid.


## Billing

<img width="1910" height="962" alt="image" src="https://github.com/user-attachments/assets/7bc3db7f-f5d2-4e31-a2a1-dbf638444000" />

## Inventory

<img width="1910" height="921" alt="image" src="https://github.com/user-attachments/assets/9a863ba6-2d2e-48d1-9ca3-9b8f62272920" />


## Customers

<img width="1916" height="971" alt="image" src="https://github.com/user-attachments/assets/bbebe60e-f360-479d-9035-d4911a14df94" />

## Payments and credits

<img width="1917" height="922" alt="image" src="https://github.com/user-attachments/assets/8432e0ed-9189-4248-93fa-69a2025b297c" />

## Bill / Transaction History

<img width="1901" height="968" alt="image" src="https://github.com/user-attachments/assets/b7848f0a-e095-4c8c-9e78-c2d14b7189c4" />

## AI Assistant

<img width="1906" height="920" alt="image" src="https://github.com/user-attachments/assets/6f23b344-de3f-48fd-aaca-7fa6cee73d2b" />

<img width="1911" height="946" alt="image" src="https://github.com/user-attachments/assets/4ee40450-7916-4a8b-8449-da3f8cd6fd98" />

## Result for the above Query

<img width="1917" height="970" alt="image" src="https://github.com/user-attachments/assets/de1ea7a1-5e37-4981-ba16-063b348628f4" />
<img width="1912" height="890" alt="image" src="https://github.com/user-attachments/assets/51802262-8f44-4869-a407-8383bf0bdefe" />

## AI Tools

The current agent exposes nine business tools:

| Tool | Purpose |
|---|---|
| `check_stock` | Check current stock for a product |
| `receive_stock` | Add received inventory |
| `low_stock` | Find products at or below reorder level |
| `create_bill` | Validate stock, calculate GST and create a bill |
| `add_customer` | Create a customer record |
| `add_credit` | Add an amount to a customer's Khata balance |
| `add_payment` | Record a customer payment |
| `get_balance` | Check a customer's outstanding balance |
| `get_bill_history` | Retrieve previous bills |

> **Note:** `get_bill_history` is included in the current implementation, making the active tool surface nine named operations in total.

## Example AI Commands

```text
Check the stock of Maggi 70g
```

```text
Create a bill for 2 Maggi 70g packets and pay by cash
```

```text
Add customer Ravi with phone number 9876543210
```

```text
How much does Ravi owe?
```

```text
Add ₹500 credit to Ravi
```

```text
Record a payment of ₹200 from Ravi
```

```text
Show previous bills
```

The agent can chain operations when a request requires multiple steps. For example, a billing request can first check stock and then attempt bill creation based on the tool result.

## Architecture

```text
                    ┌──────────────────────┐
                    │   Streamlit UI       │
                    │  Command Center      │
                    │  Billing / Inventory │
                    │  Customers / Credit  │
                    │  AI Assistant        │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     AI Agent         │
                    │    src/agent.py      │
                    │                      │
                    │ Gemini + Tool Calling│
                    └──────────┬───────────┘
                               │
                ┌──────────────┼──────────────┐
                ▼              ▼              ▼
          Inventory         Billing       Customers
            Tools            Tools          / Khata
                └──────────────┼──────────────┘
                               ▼
                    ┌──────────────────────┐
                    │      SQLite DB       │
                    │ database/supermarket │
                    │       .db            │
                    └──────────────────────┘
```

### Main Components

- `ui/app.py` — Streamlit application and operations dashboard
- `src/agent.py` — Gemini model integration, function definitions and tool-calling loop
- `src/tools/products.py` — inventory operations
- `src/tools/billing.py` — billing and stock validation
- `src/tools/customers.py` — customer and Khata operations
- `src/tools/bill_history.py` — previous bill retrieval
- `src/tools/registry.py` — tool registration utilities
- `src/database.py` — SQLite connection
- `database/schema.sql` — database schema

## Agent Control Loop

The agent follows a model → tool → result → model control loop:

1. The operator sends a natural-language request.
2. Gemini interprets the request.
3. Gemini selects a registered function when an operation is required.
4. The application executes the corresponding Python business function.
5. The tool result is returned to Gemini.
6. Gemini can select another tool when the task requires multiple operations.
7. Gemini produces the final response.

The execution timeline uses the optional trace callback to expose these steps in the UI.

## Business Rules

Important business logic is enforced in the tool/database layer rather than relying only on the model prompt.

### Stock Validation

A bill cannot be created when requested quantity exceeds available stock. This prevents overselling at the operation layer.

### Inventory Updates

Successful sales reduce product quantity through the billing operation.

### GST

Billing uses the product's configured GST rate and calculates the corresponding tax values used by the application.

### Khata / Customer Credit

Customers can maintain an outstanding balance through:

- Credit additions
- Payments
- Balance queries

### Database Grounding

Product availability, prices, customer balances and bill history are retrieved from SQLite through application tools rather than invented by the model.

## Project Structure

```text
nebula-supermarket-ops-agent/
│
├── database/
│   └── schema.sql
│
├── src/
│   ├── agent.py
│   ├── database.py
│   ├── main.py
│   ├── gemini_test.py
│   └── tools/
│       ├── __init__.py
│       ├── registry.py
│       ├── products.py
│       ├── billing.py
│       ├── customers.py
│       └── bill_history.py
│
├── ui/
│   └── app.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/VIJAYARAGAVAN-K/nebula-supermarket-ops-agent.git
cd nebula-supermarket-ops-agent
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Gemini

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Do not commit `.env` or API keys to GitHub.

### 5. Initialize the database

Ensure the SQLite database is initialized using the project's schema/data setup. The application expects the database at:

```text
database/supermarket.db
```

The `.gitignore` excludes `*.db` so local database files are not committed.

### 6. Start the application

```bash
streamlit run ui/app.py
```

Then open the local Streamlit URL shown in the terminal.

## Deployment

The Streamlit UI can be deployed using **Streamlit Community Cloud** with the GitHub repository.

For deployment, configure the Gemini key through the platform's secrets configuration rather than committing a `.env` file.

Recommended entry point:

```text
ui/app.py
```

## Error Handling

The application includes handling for common operational failures such as:

- Missing Gemini API key
- Gemini/API quota errors
- Tool execution failures
- Database failures
- Insufficient stock during billing
- Missing customer information for credit operations

## Design Decisions & Trade-offs

### Gemini Function Calling

**Decision:** Use Gemini function calling rather than a manually coded intent router.

**Why:** The model can interpret varied natural-language requests and select tools dynamically, while deterministic business logic remains inside Python tools.

**Trade-off:** Model/API availability and latency are introduced into the interaction flow. Tool validation therefore remains essential.

### SQLite

**Decision:** Use SQLite for the current prototype.

**Why:** It is lightweight, local, easy to deploy and sufficient for a small supermarket demonstration.

**Trade-off:** A production multi-user deployment would require a stronger transactional/concurrent database architecture.

### Streamlit

**Decision:** Use Streamlit for the current operations dashboard.

**Why:** It enables rapid development of a professional internal operations interface while keeping the focus on the AI agent and business logic.

**Trade-off:** It is not intended to replace a full production frontend architecture for a large multi-user application.

### Tool-Level Business Rules

**Decision:** Keep stock and customer/business rules inside tools rather than depending on prompt instructions.

**Why:** The model should orchestrate operations, not be trusted as the final authority for data integrity.

## Current Scope

The current implementation focuses on **Features 1–7**:

1. KPI Dashboard
2. Sales & Revenue Analytics
3. Top-Selling Products
4. Low-Stock Alert Center
5. Recent Activity Timeline
6. AI Operations Panel
7. AI Execution Timeline

Telegram integration is **not part of the current implementation** and is intentionally left for a future iteration.

## Future Improvements

With more development time, the project could be extended with:

- Telegram interface integration
- Multi-turn bill/cart state
- Stronger transaction and concurrency controls
- Idempotent billing operations
- PDF GST invoice generation
- Automated business-analysis reports
- Persistent operator preferences
- Multi-language support including Hindi/Tamil
- Barcode/product-photo identification
- Production-grade authentication and role-based access
- PostgreSQL or another production database
- Automated tests and CI/CD

## Validation Example

A useful safety test is:

```text
User:
Create a bill for 100 Maggi 70g packets and pay by cash.
```

Expected behavior:

```text
Gemini
  ↓
check_stock
  ↓
Stock result
  ↓
create_bill
  ↓
Insufficient stock / safe rejection
  ↓
Final response
```

The system should not silently create a bill for inventory that is unavailable.

## Technology Stack

- **Python**
- **Google Gemini**
- **Gemini Function Calling / Interactions API**
- **Streamlit**
- **SQLite**
- **Plotly** (where available for analytics visualization)
- **python-dotenv**

## Project Status

**Status: Active prototype / hiring-task implementation**

