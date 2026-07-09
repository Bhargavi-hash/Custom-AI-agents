# import requests
import json
# from dotenv import load_dotenv
from openai import OpenAI

# load_dotenv()

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

def calculate_add(a: int, b: int) -> str:
    result = a+b
    return f"The calculation result is {result}"

tools_definition = [
    {
        "type": "function",
        "function": {
            "name": "calculate_add",
            "description": "Use this function to add two numbers together.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "integer",
                        "description": "The first number"
                    },
                    "b": {
                        "type": "integer",
                        "description": "The second number"
                    }
                },
                "required": ["a", "b"]
            }
        }
    }
]

messages = [
    {"role": "user", "content": "Can you add 1234 and 457?"}
]

print("Sending the prompt to the Agent ...")

response = client.chat.completions.create(
    model="llama3.2:1b",
    messages=messages,
    tools=tools_definition,
    # tool_choice="auto"
)

response_message = response.choices[0].message

if response_message.tool_calls:
    print("\n🤖 Agent: 'I need to use a tool to solve this.'")

    tool_call = response_message.tool_calls[0]
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)

    print(f"👉 Tool Requested: {function_name}")
    print(f"👉 Arguments Extracted: {function_args}")

    if function_name == 'calculate_add':
        tool_output = calculate_add(a=int(function_args["a"]), b=int(function_args["b"]))
        print(f"\n⚙️ Executed tool successfully! Output: {tool_output}")

        messages.append(response_message)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": function_name,
            "content": tool_output
        })

        final_response = client.chat.completions.create(
            model="llama3.2:1b",
            messages=messages
        )

        print("\n--- Final Agent Answer ---")
        print(final_response.choices[0].message.content)
else:
    # If no tool was needed, just print the text answer
    print("\n--- Agent Answer (No tool used) ---")
    print(response_message.content)



