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
def fetch_weather_by_coords(lat: float, lon: float, days: int = 1):
    """
    Calls WeatherAPI using numeric coordinates.
    Caches results by rounded float coordinates.
    """
    cache_key = (round(lat, 4), round(lon, 4), days)
    if cache_key in weather_cache:
        return weather_cache[cache_key]

    url = f"{config.WEATHER_BASE_URL}/forecast.json"
    params = {
        "key": config.WEATHER_API_KEY,
        "q": f"{lat},{lon}",
        "days": days,
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
@router.get("/weather") # Real time weather endpoint
def get_weather(
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
            "tz_id": location.get("tz_id"),
            "temperature_C": current.get("temp_c"),
            "humidity": current.get("humidity"),
            "windspeed_kph": current.get("wind_kph"),
            "condition": current.get("condition", {}),
            "pressure_mb": current.get("pressure_mb"),
            "air_quality": current.get("air_quality", {})
        }

        return simplified

    except KeyError:
        # This should rarely happen unless WeatherAPI changes its schema.
        raise HTTPException(status_code=500, detail="Unexpected WeatherAPI response format.")

@router.get('/weather/forecast')
def get_weather_forecast(
    q: str = Query(..., description="City name, 'lat,lon', zip, iata, etc."),
    days: int = Query(1, ge=1, le=10, description="Number of forecast days (1-10)")
):
    """
    Fetches weather forecast for the specified number of days
    using a flexible query.
    """
    data = fetch_weather_by_q(q, days)
    
    try:
        location = data['location']
        forecast_days = data.get("forecast", {}).get('forecastday', [])
        
        simpified_forecast = []
        for days in forecast_days:
            day_info = days.get('day', {})
            simpified_forecast.append({
                "date": days.get('date'),
                "max_temp_C": day_info.get('maxtemp_c'),
                "min_temp_C": day_info.get('mintemp_c'),
                "avg_temp_C": day_info.get('avgtemp_c'),
                "condition": day_info.get('condition', {}).get('text'),
                "max_wind_kph": day_info.get('maxwind_kph'),
                "total_precip_mm": day_info.get('totalprecip_mm'),
                "avg_humidity": day_info.get('avghumidity'),
                "condition": day_info.get('condition', {}),
            })
        
        return {
            "city": location.get("name"),
            "country": location.get("country"),
            "lat": location.get("lat"),
            "lon": location.get("lon"),
            "forecast": simpified_forecast
        }
    except KeyError:
        raise HTTPException(status_code=500, detail="Unexpected WeatherAPI response format.")
    

