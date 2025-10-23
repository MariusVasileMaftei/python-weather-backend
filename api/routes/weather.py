from fastapi import APIRouter, HTTPException, Query
import requests
from core.config import config
from cachetools import TTLCache, cached

router = APIRouter()

# Cache: max 100 intrări, fiecare valabilă 10 minute
weather_cache = TTLCache(maxsize=100, ttl=600)

@cached(weather_cache)
def fetch_weather(
    city: str,
    days: int = 1,
    aqi: str = "yes",
    alerts: str = "yes",
    pollen: str = "yes",
    current_fields: str = "temp_c,wind_mph",
    wind100kph: str = "yes"
):
    """Preia datele meteo de la WeatherAPI și le memorează în cache"""
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
        raise HTTPException(status_code=response.status_code, detail="Eroare la interogarea WeatherAPI")
    return response.json()


@router.get("/weather/{city}")
def get_weather(
    city: str,
    days: int = Query(1, ge=1, le=10),
    aqi: str = Query("yes"),
    alerts: str = Query("yes"),
    pollen: str = Query("yes"),
    current_fields: str = Query("temp_c,wind_mph"),
    wind100kph: str = Query("yes")
):
    """Returnează vremea curentă și prognoza pentru un oraș, cu parametri opționali"""
    data = fetch_weather(
        city=city,
        days=days,
        aqi=aqi,
        alerts=alerts,
        pollen=pollen,
        current_fields=current_fields,
        wind100kph=wind100kph
    )

    current_data = data.get("current", {})
    forecast_day = data.get("forecast", {}).get("forecastday", [{}])[0]

    # Extragem polen doar dacă există
    pollen_data = None
    if "day" in forecast_day and "pollen" in forecast_day["day"]:
        pollen_data = forecast_day["day"]["pollen"]

    return {
        "oras": data.get("location", {}).get("name"),
        "tara": data.get("location", {}).get("country"),
        "temperatura_C": current_data.get("temp_c"),
        "conditii": current_data.get("condition", {}).get("text"),
        "wind_kph": current_data.get("wind_kph"),
        "wind_mph": current_data.get("wind_mph"),
        "pollen": pollen_data,
        "prognoza_zile": [
            {
                "data": d.get("date"),
                "max_temp_C": d.get("day", {}).get("maxtemp_c"),
                "min_temp_C": d.get("day", {}).get("mintemp_c"),
                "conditii": d.get("day", {}).get("condition", {}).get("text")
            }
            for d in data.get("forecast", {}).get("forecastday", [])
        ]
    }
