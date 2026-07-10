from db import init_db, get_total, update_expense, delete_expense, add_expense, list_expenses
from google import genai
from dotenv import load_dotenv
from eval_cases import test_cases
from datetime import date

load_dotenv()

TEST_DB = "test.db"
init_db(TEST_DB)  # or init_db(TEST_DB) once db.py supports a db_path parameter

client = genai.Client()
available_tools = {
    "get_total": get_total, "update_expense": update_expense,
    "delete_expense": delete_expense, "add_expense": add_expense,
    "list_expenses": list_expenses,
}
tools = list(available_tools.values())

def args_match(actual, expected):
    return all(actual.get(k) == v for k, v in expected.items())

passed = 0
for tc in test_cases:
    contents = []  # fresh per test case
    today_str = date.today().isoformat()
    contents.append(
        genai.types.Content(role="user", parts=[genai.types.Part(text=f"Today's date is {today_str}. {tc['query']}")])
    )

    response = client.models.generate_content(
        model='gemini-3.1-flash-lite',
        contents=contents,
        config=genai.types.GenerateContentConfig(
            tools=tools,
            automatic_function_calling=genai.types.AutomaticFunctionCallingConfig(disable=True)
        )
    )

    if not response.function_calls:
        print(f"FAILED: '{tc['query']}' — no tool called")
        continue

    fc = response.function_calls[0]
    tool_ok = fc.name == tc["expected_tool"]
    args_ok = args_match(fc.args, tc["expected_args"])

    if tool_ok and args_ok:
        passed += 1
        print(f"PASSED: '{tc['query']}'")
    else:
        print(f"FAILED: '{tc['query']}' — tool={fc.name} (expected {tc['expected_tool']}), args={dict(fc.args)}")

print(f"\n{passed}/{len(test_cases)} passed")