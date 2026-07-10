from google import genai
import os
from dotenv import load_dotenv
from db import add_expense, get_total, list_expenses, delete_expense

load_dotenv()

client = genai.Client()

available_tools = {
    "add_expense": add_expense,
    "get_total": get_total,
    "list_expenses": list_expenses,
    "delete_expense": delete_expense
}

contents = []

print("--------- Personal Expense Tracker ------------")

while True:
    user_query = input("User > ")
    if user_query == "/bye":
        print("-----------Closing session----------")
        break

    contents.append(
        genai.types.Content(role="user", parts=[genai.types.Part(text=f"{user_query}")])
    )
    
    response = client.models.generate_content(
        model='gemini-3.1-flash-lite',
        contents=contents,
        config=genai.types.GenerateContentConfig(
            tools=[add_expense, get_total, list_expenses, delete_expense],
            automatic_function_calling=genai.types.AutomaticFunctionCallingConfig(disable=True)
        )
    )

    if response.function_calls:
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
                            name=function_call.name,
                            response={"result": result}
                        )
                    ]
                )
            )
        print("All tool calls executed!")

        final_response = client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=contents,
            config=genai.types.GenerateContentConfig(
                tools=[add_expense, get_total, list_expenses, delete_expense],
                automatic_function_calling=genai.types.AutomaticFunctionCallingConfig(disable=True)
            )
        )
        contents.append(final_response.candidates[0].content)
        print(f"Model > {final_response.text}")

    else: 
        print(f"Model > {response.text}")
        contents.append(response.candidates[0].content)






