import os
import json
from dotenv import load_dotenv
from google import genai

from src.tools.products import check_stock

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
    }
]

interaction = client.interactions.create(
    model="gemini-3.6-flash",
    input="How many Maggi products are currently in stock?",
    tools=tools
)

for step in interaction.steps:
    if step.type == "function_call":
        print("Gemini requested:", step.name)

        result = check_stock(step.arguments["product_name"])

        final_interaction = client.interactions.create(
            model="gemini-3.6-flash",
            previous_interaction_id=interaction.id,
            tools=tools,
            input=[
                {
                    "type": "function_result",
                    "name": step.name,
                    "call_id": step.id,
                    "result": [
                        {
                            "type": "text",
                            "text": json.dumps({"result": result})
                        }
                    ]
                }
            ]
        )

        print("Agent:", final_interaction.output_text)