import requests
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

OPEN_WEATHER_API_KEY = os.getenv("OPEN_WEATHER_API_KEY")

def get_pos(city: str):
    try:
        response = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=5&appid={OPEN_WEATHER_API_KEY}")
        data = response.json()
        print(f"For {city} the latitude is {data[0]['lat']} and longitude is {data[0]['lon']}")

        return (data[0]['lat'], data[0]['lon'])
    
    except Exception as e:
        print(f"Something went wrong while fetching the location on map. Error: {e}")


# Defining weather tool function
def get_weather(city: str) -> dict:

    """
        Gets the current temperature of a give location

        Args:
            city: The city name, e.g. London or Santa Barbara
    """
    
    try:
        lat, lon = get_pos(city)
        print(f"Fetching weather details for {city}")
        # response = requests.get(f"https://api.openweathermap.org/data/1.0/onecall/current?lat={lat}&lon={lon}&appid={OPEN_WEATHER_API_KEY}")
        # data = response.json()
        # print(data)
        return {
            "Temperature": 22,
            "Pressure": 52,
            "Humidity": 15.3,
            "Weather": "Clear Sky"
        }
    except Exception as e:
        print(f"Something went wrong in featching weather. Error: {e}")

tools_available = {
    "get_weather": get_weather
}


print("---------- Weather AI agent -------------")
contents = []
client = genai.Client()


while True:

    user_query = input("User (Type '/bye' to exit) > ")

    if user_query == "/bye":
        print("----------- Closing the session -------------")
        break

    contents.append(
        genai.types.Content(role="user", parts=[genai.types.Part(text=f"{user_query}")])
    )

    response = client.models.generate_content(
        model='gemini-3.1-flash-lite',
        contents=contents,
        config=genai.types.GenerateContentConfig(
            tools=[get_weather],
            automatic_function_calling=genai.types.AutomaticFunctionCallingConfig(disable=True)
        )
    )

    if response.function_calls:
        for function_call in response.function_calls:
            print(f"Model want to call: {function_call.name}")
            print(f"With arguments: {function_call.args}")

            tool_function = tools_available[function_call.name]
            tool_args = function_call.args

            data = tool_function(**tool_args)
            temp = data["Temperature"]
            print(f"Temperature: {temp}" )

            contents.append(response.candidates[0].content)

            contents.append(
                genai.types.Content(
                    role="user",
                    parts=[
                        genai.types.Part.from_function_response(
                            name=function_call.name,
                            response={"result": data}
                        )
                    ]
                )
            )

            final_response = client.models.generate_content(
                model='gemini-3.1-flash-lite',
                contents=contents,
                config=genai.types.GenerateContentConfig(tools=[get_weather])
            )

            print(f"Model > {final_response.text}")

            contents.append(final_response.candidates[0].content)
            

    else:
        print(f"Model > {response.text}")
        contents.append(response.candidates[0].content) 




# Setup the LLM brain
# Define the tool with fetching feature from Open weather
# Let AI do the tool call when needed.