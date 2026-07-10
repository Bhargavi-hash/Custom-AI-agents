from google import genai
from datetime import datetime
from dotenv import load_dotenv
from tools import list_events, create_event, update_event, delete_event, get_meeting_stats, compare_periods, find_free_time

load_dotenv()
client = genai.Client()

available_tools = {
    'list_events': list_events, 'create_event': create_event,
    'update_event': update_event, 'delete_event': delete_event,
    'get_meeting_stats': get_meeting_stats, 'compare_periods': compare_periods,
    'find_free_time': find_free_time
}
all_tools = list(available_tools.values())

def get_agent_response(user_query: str, contents: list) -> str:
    """Sends a user query through the full tool-calling loop, mutates
    `contents` in place with the full history, and returns the final
    text answer."""
    now = datetime.now().astimezone()
    context_prefix = f"Right now it is {now.isoformat()}. "

    contents.append(
        genai.types.Content(role="user", parts=[genai.types.Part(text=f"{context_prefix}{user_query}")])
    )

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
            contents.append(response.candidates[0].content)
            return response.text

        for function_call in response.function_calls:
            tool_name = function_call.name
            tool_args = function_call.args
            tool = available_tools[tool_name]
            result = tool(**tool_args)

            contents.append(response.candidates[0].content)
            contents.append(
                genai.types.Content(
                    role="user",
                    parts=[genai.types.Part.from_function_response(name=tool_name, response={"result": result})]
                )
            )

