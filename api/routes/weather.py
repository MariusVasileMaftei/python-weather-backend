from fastapi import APIRouter, HTTPException, Query
import requests
from core.config import config
from cachetools import TTLCache

router = APIRouter()

# Simple cache so we don’t hit WeatherAPI with the same request over and over.
# 10 min TTL seems fine for weather data.
weather_cache = TTLCache(maxsize=100, ttl=600)

# -------------------------------
# Function that calls WeatherAPI using any type of query
# -------------------------------
def fetch_weather_by_q(q: str, days: int = 1):
    """
    This handles all WeatherAPI query formats (city, coords, zip, iata, etc.).
    Keeping cache per (query, days) because people might request different durations.
    """
    cache_key = (q.lower(), days)
    if cache_key in weather_cache:
        return weather_cache[cache_key]

    url = f"{config.WEATHER_BASE_URL}/forecast.json"
    params = {
        "key": config.WEATHER_API_KEY,
        "q": q,
        "days": days,
        "aqi": "yes",    # keeping AQI enabled so we have complete data
        "alerts": "yes"  # same for weather alerts
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        # Just forward the WeatherAPI error so we can see exactly what they return
        raise HTTPException(
            status_code=response.status_code,
            detail=f"WeatherAPI Error {response.status_code}: {response.text}"
        )

    data = response.json()
    weather_cache[cache_key] = data
    return data


# -------------------------------
# Function specifically for numeric coords
# -------------------------------
def fetch_weather_by_coords(lat: float, lon: float):
    """
    Same logic as above but meant for direct float coords.
    Rounding for the cache key just avoids treating tiny float differences
    as completely different locations.
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
        # Again, forwarding the real API error so it’s easier to debug
        raise HTTPException(
            status_code=response.status_code,
            detail=f"WeatherAPI Error {response.status_code}: {response.text}"
        )

    data = response.json()
    weather_cache[cache_key] = data
    return data


# -------------------------------
# Main universal endpoint
# -------------------------------
@router.get("/weather")
def get_weather(
    q: str = Query(..., description="WeatherAPI query: city name, 'lat,lon', zip, iata, auto:ip, etc."),
    days: int = Query(1, ge=1, le=10)
):
    """
    This endpoint is basically a wrapper so the client can send
    any valid WeatherAPI query string without us enforcing the format.
    """
    return fetch_weather_by_q(q, days)


# -------------------------------
# Separate endpoint just for Swagger (coords)
# -------------------------------
@router.get("/weather/coords")
def get_weather_by_coords(
    coords: str = Query(..., description="Coordinates as 'lat,lon', e.g., '44.4328,26.1043'")
):
    """
    Swagger handles a single string input much nicer than two separate numeric fields,
    so this endpoint exists mainly for easier testing. We parse the string manually.
    """
    try:
        lat_str, lon_str = coords.split(",")
        lat = float(lat_str.strip())
        lon = float(lon_str.strip())
    except ValueError:
        # In case someone enters something like "bla bla", give them a clear error
        raise HTTPException(status_code=400, detail="Invalid coordinates format. Use 'lat,lon'.")

    return fetch_weather_by_coords(lat, lon)
