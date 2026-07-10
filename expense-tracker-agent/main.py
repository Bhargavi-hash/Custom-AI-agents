from google import genai
import os
from datetime import date
from dotenv import load_dotenv
from db import add_expense, get_total, list_expenses, delete_expense, update_expense

load_dotenv()
client = genai.Client()

available_tools = {
    "add_expense": add_expense,
    "get_total": get_total,
    "list_expenses": list_expenses,
    "delete_expense": delete_expense,
    "update_expense": update_expense,
}

all_tools = [add_expense, get_total, list_expenses, delete_expense, update_expense]

contents = []
print("--------- Personal Expense Tracker ------------")

while True:
    user_query = input("User > ")
    if user_query == "/bye":
        print("-----------Closing session----------")
        break

    today_str = date.today().isoformat()
    contents.append(
        genai.types.Content(
            role="user",
            parts=[genai.types.Part(text=f"Today's date is {today_str}. {user_query}")]
        )
    )

    # Keep looping until Gemini returns plain text with no more function calls pending.
    # A single user turn might need zero, one, or several chained tool calls.
    while True:
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=contents,
            config=genai.types.GenerateContentConfig(
                tools=all_tools,
                automatic_function_calling=genai.types.AutomaticFunctionCallingConfig(disable=True)
            )
        )

        if not response.function_calls:
            # No more tools needed -- this is the real final answer for this turn
            contents.append(response.candidates[0].content)
            print(f"Model > {response.text}")
            break

        # Otherwise, execute this round of tool call(s), then loop again
        for function_call in response.function_calls:
            tool_name = function_call.name
            tool_args = function_call.args
            print(f"Model needs {tool_name} tool")

            tool = available_tools[tool_name]
            result = tool(**tool_args)
            print(result)

            contents.append(response.candidates[0].content)
            contents.append(
                genai.types.Content(
                    role="user",
                    parts=[
                        genai.types.Part.from_function_response(
                            name=tool_name,
                            response={"result": result}
                        )
                    ]
                )
            )
        print("Tool call round executed, checking if more are needed...")