from fastapi import APIRouter, HTTPException, Query
import requests
from core.config import config
from cachetools import TTLCache

router = APIRouter()

# --------------------------------------------------------------
# In-memory TTL cache for WeatherAPI responses.
# - Prevents repeated calls for the same location.
# - TTL = 10 minutes (reasonable for weather data).
# - maxsize = 100 entries.
# --------------------------------------------------------------
weather_cache = TTLCache(maxsize=100, ttl=600)


# --------------------------------------------------------------
# Fetch weather using WeatherAPI's flexible "q" parameter.
# Accepts:
#   - City name (e.g., "London")
#   - Coordinates (e.g., "44.43,26.10")
#   - ZIP code
#   - Airport IATA
#   - auto:ip
#
# This function:
#   - Uses caching to reduce API calls.
#   - Forwards WeatherAPI errors to the client.
# --------------------------------------------------------------
def fetch_weather_by_q(q: str, days: int = 1):
    """
    Calls WeatherAPI using arbitrary query formats (q parameter).
    Caches results for (query, days).
    """
    cache_key = (q.lower(), days)
    if cache_key in weather_cache:
        return weather_cache[cache_key]

    url = f"{config.WEATHER_BASE_URL}/forecast.json"
    params = {
        "key": config.WEATHER_API_KEY,
        "q": q,
        "days": days,
        "aqi": "yes",     # Include Air Quality Index for richer data.
        "alerts": "yes"   # Include weather alerts.
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        # Pass through WeatherAPI error response for debugging transparency.
        raise HTTPException(
            status_code=response.status_code,
            detail=f"WeatherAPI Error {response.status_code}: {response.text}"
        )

    data = response.json()
    weather_cache[cache_key] = data
    return data


# --------------------------------------------------------------
# Fetch weather using explicit latitude and longitude values.
# This version:
#   - Rounds lat/lon to 4 decimals to prevent caching identical
#     points with tiny float differences.
#   - Returns the raw WeatherAPI structure.
# --------------------------------------------------------------
def fetch_weather_by_coords(lat: float, lon: float):
    """
    Calls WeatherAPI using numeric coordinates.
    Caches results by rounded float coordinates.
    """
    cache_key = (round(lat, 4), round(lon, 4))
    if cache_key in weather_cache:
        return weather_cache[cache_key]

    url = f"{config.WEATHER_BASE_URL}/forecast.json"
    params = {
        "key": config.WEATHER_API_KEY,
        "q": f"{lat},{lon}",
        "days": 1,
        "aqi": "yes",
        "alerts": "yes"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"WeatherAPI Error {response.status_code}: {response.text}"
        )

    data = response.json()
    weather_cache[cache_key] = data
    return data


# --------------------------------------------------------------
# MAIN WEATHER ENDPOINT (Simplified version)
#
# Returns only the essential fields:
#   - city, country
#   - lat, lon
#   - temperature in C
#   - humidity
#   - wind speed (kph)
#   - weather condition text
#
# This keeps responses lightweight and easy for frontend use.
# --------------------------------------------------------------
@router.get("/weather")
def get_simple_weather(
    q: str = Query(..., description="City name, 'lat,lon', zip, iata, etc.")
):
    """
    Fetches weather using a flexible query and returns a simplified
    subset of the WeatherAPI response, focusing on core metrics.
    """
    data = fetch_weather_by_q(q)

    try:
        location = data["location"]
        current = data["current"]

        simplified = {
            "city": location.get("name"),
            "country": location.get("country"),
            "lat": location.get("lat"),
            "lon": location.get("lon"),
            "temperature_C": current.get("temp_c"),
            "humidity": current.get("humidity"),
            "windspeed_kph": current.get("wind_kph"),
            "condition": current.get("condition", {}).get("text"),
        }

        return simplified

    except KeyError:
        # This should rarely happen unless WeatherAPI changes its schema.
        raise HTTPException(status_code=500, detail="Unexpected WeatherAPI response format.")


# --------------------------------------------------------------
# OPTIONAL ENDPOINT: Fetch weather by coordinate string.
# Useful in Swagger UI since it handles single-string params better.
#
# Example call:
#     /weather/coords?coords=44.4328,26.1043
#
# (Currently commented out to avoid extra endpoints unless needed.)
# --------------------------------------------------------------
'''
@router.get("/weather/coords")
def get_weather_by_coords(
    coords: str = Query(..., description="Coordinates as 'lat,lon', e.g., '44.4328,26.1043'")
):
    """
    Parses a 'lat,lon' string and fetches weather from coordinates.
    """
    try:
        lat_str, lon_str = coords.split(",")
        lat = float(lat_str.strip())
        lon = float(lon_str.strip())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid coordinates format. Use 'lat,lon'.")

    return fetch_weather_by_coords(lat, lon)
'''
