from google import genai
from datetime import datetime
from dotenv import load_dotenv
from tools import list_events, create_event, update_event, delete_event, get_meeting_stats, compare_periods, find_free_time

load_dotenv()
client = genai.Client()

available_tools = {
    'list_events': list_events,
    'create_event': create_event,
    'update_event': update_event,
    'delete_event': delete_event,
    'get_meeting_stats': get_meeting_stats,
    'compare_periods': compare_periods,
    'find_free_time': find_free_time
}

all_tools = list(available_tools.values())  # same functions, as a list, for the `tools=` config

contents = []
print("--------- Calendar Agent ------------")

while True:
    user_query = input("User > ")
    if user_query == "/bye":
        break

    # Hint: you need something like this for every prompt now:
    now = datetime.now().astimezone()
    context_prefix = f"Right now it is {now.isoformat()}. "
    # ^ .astimezone() with no args converts to your LOCAL system timezone, 
    #   and .isoformat() on a timezone-aware datetime includes the offset 
    #   automatically (e.g., "...T14:32:07-07:00") -- this gives Gemini 
    #   both the current date/time AND the correct offset to use

    contents.append(
        genai.types.Content(role="user", parts=[genai.types.Part(text=f"{context_prefix}{user_query}")])
    )

    # Same "loop until no more function calls" pattern from your expense tracker
    while True:
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=contents,
            config=genai.types.GenerateContentConfig(
                tools=all_tools,
                automatic_function_calling=genai.types.AutomaticFunctionCallingConfig(disable=True)
            )
        )
        # ... fill in the rest, reusing your expense tracker's structure exactly

        if not response.function_calls:
            print(f"Model > {response.text}")
            contents.append(response.candidates[0].content)
            break
        
        for function_call in response.function_calls:
            tool_name = function_call.name
            tool_args = function_call.args

            print(f"Model needs to call {tool_name}.")

            tool = available_tools[tool_name]
            result = tool(**tool_args)

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






