import os
import json
from openai import OpenAI

MAX_INTERNAL_LOOP = 3
MAX_EXTERNAL_LOOP = 5

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

tools = [
    {
        "type": "function",
        "name": "query_db",
        "description": "Query database with customer information",
        "parameters": {
            "type": "object",
            "properties": {
                "order_number": {
                    "type": "integer",
                    "description": "number associated to customers orders",
                },
            },
            "required": ["order_number"],
        },
    },
]


def query_db(order_number):
    return "PENDING"


def main():
    print("Hello from agentic-chatbot!")

    input_list = [
        {"role": "system", "content": "You are a customer service advocate."},
        # {"role": "user", "content": "What is the status of my order?"},
    ]
    external_loop = 0
    while external_loop < MAX_EXTERNAL_LOOP:
        external_loop += 1
        # get user input
        input_text = input("USER: ")
        if input_text == "STOP":
            break
        input_list.append({"role": "user", "content": input_text})

        # generate response
        internal_loop = 0
        answered = False
        while internal_loop < MAX_INTERNAL_LOOP and answered is False:
            internal_loop += 1
            response = client.responses.create(
                model="gpt-5.4-mini",   # or gpt-5.4-nano
                tools=tools,
                input=input_list,
            )
            input_list += response.output

            # process tool calls
            for item in response.output:
                if item.type == "function_call":
                    if item.name == "query_db":
                        status = query_db(json.loads(item.arguments))
                        # Save function call outputs for subsequent requests
                        input_list.append({
                            "type": "function_call_output",
                            "call_id": item.call_id,
                            "output": json.dumps({
                              "order_status": status
                            })
                        })
                elif item.type == "message":
                    answered = True
                    print("SYSTEM: ", response.output_text)



if __name__ == "__main__":
    main()
