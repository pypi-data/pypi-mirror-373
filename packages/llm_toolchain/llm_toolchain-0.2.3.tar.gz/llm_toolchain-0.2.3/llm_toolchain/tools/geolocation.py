import requests
from ..core import tool

@tool
def get_address_from_coordinates(latitude: float, longitude: float):
    """
    Finds the street address for a given pair of latitude and longitude coordinates.

    Args:
        latitude: The latitude of the location.
        longitude: The longitude of the location.
    """
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return {"error": "Invalid latitude or longitude values."}

    # Using the free Nominatim (OpenStreetMap) API
    api_url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}"
    
    # It's good practice to set a user-agent for public APIs
    headers = {
        'User-Agent': 'ToolchainBot/1.0'
    }

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        data = response.json()

        if "error" in data:
            return {"error": data["error"]}
        
        address = data.get("display_name")
        if address:
            return {"address": address}
        else:
            return {"error": "Could not find a valid address for these coordinates."}

    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

