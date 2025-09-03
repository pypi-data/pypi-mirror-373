import requests
from ..core import tool

@tool
def get_weather(city: str, unit: str = "celsius"):
    """
    Gets the real-time current weather for a specified city using an API.

    Args:
        city: The name of the city, e.g., "San Francisco".
        unit: The temperature unit, either "celsius" or "fahrenheit".
    """
    try:
        # Step 1: Geocode the city to get latitude and longitude
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo_response = requests.get(geo_url)
        geo_response.raise_for_status()  # Raise an exception for bad status codes
        geo_data = geo_response.json()

        if not geo_data.get("results"):
            return {"error": f"Could not find coordinates for city: {city}"}

        location = geo_data["results"][0]
        latitude = location["latitude"]
        longitude = location["longitude"]
        
        # Step 2: Get the weather for the coordinates
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}"
            f"&current_weather=true&temperature_unit={unit}"
        )
        weather_response = requests.get(weather_url)
        weather_response.raise_for_status()
        weather_data = weather_response.json()

        current_weather = weather_data["current_weather"]
        temp = current_weather["temperature"]
        condition_code = current_weather["weathercode"]

        return {
            "city": location["name"],
            "temperature": f"{temp}°{unit.capitalize()[0]}",
            "condition": _get_weather_condition_from_code(condition_code)
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

def _get_weather_condition_from_code(code: int) -> str:
    """A helper to translate WMO weather codes into human-readable text."""
    codes = {
        0: "Clear sky",
        1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
        80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
        95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
    }
    return codes.get(code, "Unknown condition")

