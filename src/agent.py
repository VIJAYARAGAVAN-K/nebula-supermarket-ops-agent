import os
import json
from dotenv import load_dotenv
from google import genai
from src.tools.customers import add_customer, add_credit, add_payment, get_balance
from src.tools.products import check_stock, receive_stock, low_stock
from src.tools.billing import create_bill
from src.tools.bill_history import get_bill_history

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

tools = [
    {
        "type": "function",
        "name": "check_stock",
        "description": "Check the current inventory stock of a supermarket product.",
        "parameters": {
            "type": "object",
            "properties": {
                "product_name": {
                    "type": "string",
                    "description": "Name of the supermarket product."
                }
            },
            "required": ["product_name"]
        }
    },
    {
    "type": "function",
    "name": "add_customer",
    "description": "Add a supermarket customer.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "phone": {"type": "string"}
        },
        "required": ["name"]
    }
},
{
    "type": "function",
    "name": "add_credit",
    "description": "Add an amount to a customer's Khata credit balance.",
    "parameters": {
        "type": "object",
        "properties": {
            "customer_name": {"type": "string"},
            "amount": {"type": "number"}
        },
        "required": ["customer_name", "amount"]
    }
},
{
    "type": "function",
    "name": "add_payment",
    "description": "Record a payment made toward a customer's Khata balance.",
    "parameters": {
        "type": "object",
        "properties": {
            "customer_name": {"type": "string"},
            "amount": {"type": "number"}
        },
        "required": ["customer_name", "amount"]
    }
},
{
    "type": "function",
    "name": "get_balance",
    "description": "Check how much a customer currently owes on Khata.",
    "parameters": {
        "type": "object",
        "properties": {
            "customer_name": {"type": "string"}
        },
        "required": ["customer_name"]
    }
},
    {
        "type": "function",
        "name": "receive_stock",
        "description": "Add received quantity to an existing supermarket product's stock.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string"
                },
                "quantity": {
                    "type": "integer"
                }
            },
            "required": ["name", "quantity"]
        }
    },
    {
        "type": "function",
        "name": "low_stock",
        "description": "Find products at or below their reorder level.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
    "type": "function",
    "name": "get_bill_history",
    "description": "Show previous supermarket bills.",
    "parameters": {
        "type": "object",
        "properties": {}
        }
    },
    {
        "type": "function",
        "name": "create_bill",
        "description": "Create a bill, calculate GST, verify stock, and reduce inventory.",
        "parameters": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "sku": {
                                "type": "string"
                            },
                            "quantity": {
                                "type": "integer"
                            }
                        },
                        "required": ["sku", "quantity"]
                    }
                },
                "payment_mode": {
                    "type": "string"
                }
            },
            "required": ["items"]
        }
    }
]

function_map = {
    "check_stock": lambda args: check_stock(args["product_name"]),
    "receive_stock": lambda args: receive_stock(
        args["name"], args["quantity"]
    ),
    "low_stock": lambda args: low_stock(),
    "create_bill": lambda args: create_bill(
        args["items"],
        args.get("payment_mode", "cash")
    ),
    "add_customer": lambda args: add_customer(
        args["name"],
        args.get("phone")
    ),

    "add_credit": lambda args: add_credit(
        args["customer_name"],
        args["amount"]
    ),

"add_payment": lambda args: add_payment(
    args["customer_name"],
    args["amount"]
),
"get_bill_history": lambda args: get_bill_history(),

"get_balance": lambda args: get_balance(
    args["customer_name"]
),
}


def run_agent(user_message):

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=user_message,
        tools=tools
    )

    while True:

        function_call = None

        for step in interaction.steps:
            if step.type == "function_call":
                function_call = step
                break

        if not function_call:
            return interaction.output_text

        print("Gemini requested:", function_call.name)
        print("Arguments:", function_call.arguments)

        result = function_map[function_call.name](function_call.arguments)

        print("Tool result:", result)

        interaction = client.interactions.create(
            model="gemini-3.6-flash",
            previous_interaction_id=interaction.id,
            tools=tools,
            input=[
                {
                    "type": "function_result",
                    "name": function_call.name,
                    "call_id": function_call.id,
                    "result": [
                        {
                            "type": "text",
                            "text": json.dumps({"result": result})
                        }
                    ]
                }
            ]
        )


user_message = input("You: ")

try:
    print("Agent:", run_agent(user_message))
except Exception as e:
    if "quota" in str(e).lower() or "429" in str(e):
        print("Agent: Gemini API quota exceeded. Please try again later.")
    else:
        print("Agent error:", e)