# 🛒 Nebula Supermarket Ops Agent

An AI-powered supermarket operations management system built with **Python, Gemini AI, SQLite, and Streamlit**.

The system allows supermarket staff to manage products, inventory, customers, billing, payments, credit (Khata), bill history, and supermarket operations using both a graphical dashboard and a natural-language AI assistant.

---


## 🖥️ Application Preview

### Dashboard

<img width="1917" height="958" alt="image" src="https://github.com/user-attachments/assets/6418b8c4-f10b-4844-bee7-beec662c50b7" />


### AI Assistant

<img width="1917" height="971" alt="image" src="https://github.com/user-attachments/assets/35b519b2-5299-45f6-964a-74976a9a90f5" />


## 🚀 Features

### 🤖 AI Supermarket Assistant

Users can interact with the supermarket system using natural language.

Example requests:

text
Check the stock of Maggi 70g
Create a bill for 2 Maggi 70g packets and pay by cash.
Add customer Ravi with phone number 9876543210
How much does Ravi owe?
Add ₹500 credit to Ravi's account.
Record a payment of ₹200 from Ravi.

The AI agent identifies the required operation and calls the appropriate backend tool.

🧾 Billing

The billing system supports:

Product selection using SKU
Quantity validation
Stock verification
Automatic inventory deduction
Subtotal calculation
GST calculation
Total bill calculation
Cash payment
Credit / Khata payment
Insufficient-stock handling

Example:

Create a bill for 2 Maggi 70g packets and pay by cash.

The system checks inventory before creating the bill.

If the requested quantity is greater than available stock, the bill is rejected safely.

Example:

Requested: 100
Available: 28

The system reports insufficient stock instead of creating an invalid bill.

<img width="1917" height="972" alt="image" src="https://github.com/user-attachments/assets/df538b28-b0dc-4398-9049-270530f0f03f" />


📦 Inventory Management

The inventory module provides:

Product stock checking
Stock receiving
Low-stock detection
SKU-based product identification
Automatic stock reduction after billing

Example:

Check the stock of Maggi 70g

Possible response:

Maggi 70g | SKU: MAGGI70 | Price: ₹15.0 | Stock: 28

Stock can also be received through the AI assistant:

Receive 50 Maggi 70g packets.

<img width="1917" height="941" alt="image" src="https://github.com/user-attachments/assets/dfb1b456-431d-448f-8ab3-f1f23aee182f" />

👥 Customer Management

The customer system supports:

Adding customers
Customer name
Phone number
Credit tracking
Payment tracking
Customer balance checking

Example:

Add customer Arun with phone number 9876543210
<img width="1916" height="967" alt="image" src="https://github.com/user-attachments/assets/1f50dbdb-16d7-4c62-9e29-9451f5dda2b0" />


💳 Payments & Credit / Khata

The system supports customer credit management.

Available operations include:

Add Credit
Add ₹1000 credit to Arun.
Record Payment
Record a payment of ₹500 from Arun.
Check Balance
How much does Arun owe?

This allows the supermarket to maintain customer Khata balances.

<img width="1917" height="971" alt="image" src="https://github.com/user-attachments/assets/b80dd1cb-da7e-4193-9c79-43dd36351f60" />


📜 Bill History

The system maintains previous billing records.

The AI assistant can retrieve bill history using natural language.

Example:

Show previous bills.

The bill history module provides access to previously generated supermarket bills.
<img width="1916" height="941" alt="image" src="https://github.com/user-attachments/assets/c59f508f-a04c-4490-b78e-d84f9b7f26f5" />

<img width="1917" height="957" alt="image" src="https://github.com/user-attachments/assets/9715b8dd-d30d-44cd-adf0-3dc901b9d3db" />


📊 Streamlit Dashboard

The project includes a Streamlit-based graphical user interface.

The dashboard provides navigation for:

🏠 Dashboard
🧾 Billing
📦 Inventory
👥 Customers
💳 Payments & Credit
📜 Bill History
🤖 AI Assistant

''' The dashboard also displays basic supermarket statistics such as:

Total products
Total bills
Total customers
Low-stock products
🏗️ Project Architecture — Nebula Supermarket Ops Agent
Nebula Supermarket Ops Agent
UI
ui/app.py — Streamlit-based user interface
Source Code
src/__init__.py
src/agent.py — AI agent and Gemini integration
src/database.py — SQLite database connection
src/main.py — Application entry point
src/gemini_test.py — Gemini API testing
Tools
src/tools/__init__.py
src/tools/bill_history.py — Bill history operations
src/tools/billing.py — Billing and invoice operations
src/tools/customers.py — Customer and credit operations
src/tools/products.py — Product and inventory operations
src/tools/registry.py — Tool registry
Database
database/schema.sql — SQLite database schema
Configuration & Documentation
requirements.txt — Python dependencies
.gitignore — Git ignored files
README.md — Project documentation
🔄 System Flow

The application follows this flow:

👤 User
Enters a request using natural language.
🖥️ Streamlit UI
Receives the user's request.
Provides the interface for supermarket operations.
🤖 AI Agent
Processes the user's request.
Sends the request to Gemini AI.
🧠 Gemini AI
Understands the user's intent.
Selects the appropriate function/tool automatically.
🛠️ Function / Tool Selection
Gemini can select from the following tools:
check_stock
receive_stock
low_stock
create_bill
add_customer
add_credit
add_payment
get_balance
get_bill_history
🗄️ SQLite Database
Executes the selected operation.
Stores or retrieves supermarket data.
Updates inventory, bills, customers, payments, and credit information.
🧠 AI Agent Architecture

The AI agent is implemented in:

src/agent.py

The agent uses Gemini to determine which supermarket operation should be executed.

The available functions are registered as tools.

Available Tools
Tool	Purpose
check_stock	Check product inventory
receive_stock	Add received inventory
low_stock	Find low-stock products
create_bill	Create a supermarket bill
add_customer	Add a new customer
add_credit	Add customer credit
add_payment	Record customer payment
get_balance	Check customer balance
get_bill_history	Retrieve previous bills

The agent follows a tool-calling workflow:

User Request
     ↓
Gemini
     ↓
Select Tool
     ↓
Execute Python Function
     ↓
Database Operation
     ↓
Return Tool Result
     ↓
Gemini
     ↓
Final Response
🗄️ Database

The project uses SQLite for local data storage.

Database file:

database/supermarket.db

Database schema:

database/schema.sql

The database stores supermarket operational information including products, customers, bills, and related records.

🔐 Environment Variables

The Gemini API key is stored using an environment variable.

Create a .env file in the project root:

GEMINI_API_KEY=your_gemini_api_key

Do not commit the .env file to GitHub.

The .gitignore file already excludes environment files.

🛠️ Technologies Used
Programming Language
Python
AI
Google Gemini API
User Interface
Streamlit
Database
SQLite
Environment Management
python-dotenv
Version Control
Git
GitHub
📋 Requirements

Install the required Python packages using:

pip install -r requirements.txt

The project uses Streamlit for the web interface and the Google GenAI SDK for Gemini integration.

▶️ Running the Application
Step 1: Clone the repository
git clone <your-github-repository-url>
Step 2: Enter the project directory
cd nebula-supermarket-ops-agent
Step 3: Create a virtual environment

Windows:

python -m venv .venv
Step 4: Activate the virtual environment

PowerShell:

.venv\Scripts\Activate.ps1
Step 5: Install dependencies
pip install -r requirements.txt
Step 6: Configure Gemini API

Create:

.env

Add:

GEMINI_API_KEY=your_gemini_api_key
Step 7: Run Streamlit
streamlit run ui/app.py

The Streamlit application will open in the browser.

🧪 Example Operations
Check Stock

Input:

Check the stock of Maggi 70g

Expected behavior:

Gemini
   ↓
check_stock
   ↓
SQLite
   ↓
Stock information
Create Bill

Input:

Create a bill for 2 Maggi 70g packets and pay by cash.

Expected behavior:

Check Product
     ↓
Verify Stock
     ↓
Create Bill
     ↓
Calculate GST
     ↓
Reduce Stock
     ↓
Record Payment
Insufficient Stock

Input:

Create a bill for 100 Maggi 70g packets and pay by cash.

If only 28 packets are available:

Insufficient stock for Maggi 70g.
Available: 28

The system does not create the bill.

Customer Credit

Input:

Add customer Ravi with phone number 9876543210

Then:

Add ₹1000 credit to Ravi.

Check:

How much does Ravi owe?

Payment:

Record a payment of ₹500 from Ravi.
🖥️ User Interface

The Streamlit application provides a simple supermarket management dashboard.

Dashboard

Displays:

Products
Bills
Customers
Low Stock
Navigation
🏠 Dashboard
🧾 Billing
📦 Inventory
👥 Customers
💳 Payments & Credit
📜 Bill History
🤖 AI Assistant

The AI Assistant allows supermarket staff to perform operations without manually interacting with the database.

🔒 Security

Sensitive configuration is kept outside the source code.

The following files should not be committed:

.env
.venv/
__pycache__/
*.pyc
*.db

The .gitignore file is configured to prevent these files from being tracked.

📁 Important Files
File	Purpose
ui/app.py	Streamlit user interface
src/agent.py	Gemini AI agent and tool calling
src/database.py	SQLite database connection
src/tools/products.py	Inventory operations
src/tools/billing.py	Billing operations
src/tools/customers.py	Customer and credit operations
src/tools/bill_history.py	Bill history
src/tools/registry.py	Tool registry
database/schema.sql	Database schema
src/main.py	Main application/testing entry point
requirements.txt	Python dependencies
.env	Gemini API configuration
.gitignore	Files excluded from Git
🎯 Project Objective

The objective of the Nebula Supermarket Ops Agent is to demonstrate how an AI-powered system can simplify day-to-day supermarket operations.

Instead of requiring users to manually navigate multiple systems, the AI assistant allows them to interact with supermarket operations using natural language.

For example:

"Check Maggi stock."

"Create a bill for 5 Maggi packets."

"Add ₹500 credit to Ravi."

"Show Ravi's balance."

"Show previous bills."

The AI agent converts these requests into appropriate backend tool calls.

🔮 Future Improvements

Possible future enhancements include:

Advanced sales analytics
Product search and filtering
Invoice PDF generation
Barcode scanning
Role-based authentication
Admin dashboard
Daily sales reports
Monthly revenue analytics
Automatic stock-reorder suggestions
Multiple payment methods
Customer purchase history
Cloud database integration
Deployment to a cloud platform
👨‍💻 Development

The project follows a modular structure where supermarket operations are separated into individual tools.

This makes it easier to:

Add new supermarket operations
Modify existing tools
Test individual functions
Connect new AI capabilities
Extend the Streamlit interface
📌 Status

Project Status: Completed

Current system includes:

✅ Gemini AI Agent
✅ Function Calling
✅ SQLite Database
✅ Product Management
✅ Inventory Management
✅ Billing
✅ GST Calculation
✅ Stock Validation
✅ Customer Management
✅ Credit / Khata
✅ Payment Tracking
✅ Bill History
✅ Low Stock Detection
✅ Streamlit UI
✅ Environment Variable Configuration
✅ Git Version Control
📄 License

This project is developed as an academic/project submission.
