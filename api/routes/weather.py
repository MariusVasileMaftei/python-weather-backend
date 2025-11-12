from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
import requests
from core.config import config
from cachetools import TTLCache, cached

router = APIRouter()

# Cache: max 100 items, each valid for 10 minutes
weather_cache = TTLCache(maxsize=100, ttl=600)

# -----------------------------------
# Function to get weather by city
# -----------------------------------
@cached(weather_cache)
def fetch_weather(city: str,
                  days: int = 1,
                  aqi: str = "yes",
                  alerts: str = "yes",
                  pollen: str = "yes",
                  current_fields: str = "temp_c,wind_mph",
                  wind100kph: str = "yes"):
    """Get weather data from WeatherAPI and cache it"""
    url = f"{config.WEATHER_BASE_URL}/forecast.json"
    params = {
        "key": config.WEATHER_API_KEY,
        "q": city,
        "days": days,
        "aqi": aqi,
        "alerts": alerts,
        "pollen": pollen,
        "current_fields": current_fields,
        "wind100kph": wind100kph
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching data from WeatherAPI")
    return response.json()


# -----------------------------------
# Function to get weather by coordinates
# -----------------------------------
@cached(weather_cache)
def fetch_weather_by_coords(lat: float,
                            lon: float,
                            days: int = 1,
                            aqi: str = "yes",
                            alerts: str = "yes",
                            pollen: str = "yes",
                            current_fields: str = "temp_c,wind_mph",
                            wind100kph: str = "yes"):
    """Get weather data from WeatherAPI by latitude and longitude"""
    url = f"{config.WEATHER_BASE_URL}/forecast.json"
    params = {
        "key": config.WEATHER_API_KEY,
        "q": f"{lat},{lon}",
        "days": days,
        "aqi": aqi,
        "alerts": alerts,
        "pollen": pollen,
        "current_fields": current_fields,
        "wind100kph": wind100kph
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error fetching data from WeatherAPI")
    return response.json()


# -----------------------------------
# Endpoint to get weather by city
# -----------------------------------
@router.get("/weather/{city}")
def get_weather(city: str,
                days: int = Query(1, ge=1, le=10),
                aqi: str = Query("yes"),
                alerts: str = Query("yes"),
                pollen: str = Query("yes"),
                current_fields: str = Query("temp_c,wind_mph"),
                wind100kph: str = Query("yes")):
    """Return current weather and forecast for a city"""
    data = fetch_weather(city, days, aqi, alerts, pollen, current_fields, wind100kph)
    
    current = data.get("current", {})
    forecast_day = data.get("forecast", {}).get("forecastday", [{}])[0]

    pollen_data = forecast_day.get("day", {}).get("pollen") if "day" in forecast_day else None

    return {
        "city": data.get("location", {}).get("name"),
        "country": data.get("location", {}).get("country"),
        "temperature_C": current.get("temp_c"),
        "conditions": current.get("condition", {}).get("text"),
        "wind_kph": current.get("wind_kph"),
        "wind_mph": current.get("wind_mph"),
        "pollen": pollen_data,
        "forecast_days": [
            {
                "date": d.get("date"),
                "max_temp_C": d.get("day", {}).get("maxtemp_c"),
                "min_temp_C": d.get("day", {}).get("mintemp_c"),
                "conditions": d.get("day", {}).get("condition", {}).get("text")
            }
            for d in data.get("forecast", {}).get("forecastday", [])
        ]
    }


# -----------------------------------
# Endpoint to get weather by coordinates (changed to GET)
# -----------------------------------
@router.get("/weather/coords")
def get_weather_by_coords(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    days: int = Query(1, ge=1, le=10, description="Number of forecast days"),
    aqi: str = Query("yes", description="Include air quality"),
    alerts: str = Query("yes", description="Include weather alerts"),
    pollen: str = Query("yes", description="Include pollen data"),
    current_fields: str = Query("temp_c,wind_mph", description="Current weather fields"),
    wind100kph: str = Query("yes", description="Include wind speed in kph")
):
    """Return current weather and forecast for given coordinates"""
    data = fetch_weather_by_coords(lat, lon, days, aqi, alerts, pollen, current_fields, wind100kph)
    
    current = data.get("current", {})
    forecast_day = data.get("forecast", {}).get("forecastday", [{}])[0]

    pollen_data = forecast_day.get("day", {}).get("pollen") if "day" in forecast_day else None

    return {
        "city": data.get("location", {}).get("name"),
        "country": data.get("location", {}).get("country"),
        "temperature_C": current.get("temp_c"),
        "conditions": current.get("condition", {}).get("text"),
        "wind_kph": current.get("wind_kph"),
        "wind_mph": current.get("wind_mph"),
        "pollen": pollen_data,
        "forecast_days": [
            {
                "date": d.get("date"),
                "max_temp_C": d.get("day", {}).get("maxtemp_c"),
                "min_temp_C": d.get("day", {}).get("mintemp_c"),
                "conditions": d.get("day", {}).get("condition", {}).get("text")
            }
            for d in data.get("forecast", {}).get("forecastday", [])
        ]
    }