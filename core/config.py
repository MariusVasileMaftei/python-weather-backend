import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    PROJECT_NAME: str = "Python Weather API"
    API_VERSION: str = "v1"
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY")
    WEATHER_BASE_URL: str = "https://api.weatherapi.com/v1"

config = Config()