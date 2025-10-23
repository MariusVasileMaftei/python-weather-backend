# Python Weather Backend

Backend API for a weather web application, providing real-time weather and 5-day forecasts.  
Frontend built with Angular/Next.js by [Radu Padurariu](https://github.com/RaduPadurariu/team-project-weather-app).

---

## Tech Stack
- **Language:** Python 3.x  
- **Framework:** FastAPI  
- **Data Source:** WeatherAPI  
- **Hosting:** Render  
- **Environment:** `.env` for API keys

---

## Features
- Current weather by city or coordinates  
- 5-day forecast  
- Temperature, humidity, wind, and weather conditions  
- JSON responses for frontend integration

---

## Quick Setup
```bash
# Clone repo
git clone https://github.com/YOUR_USERNAME/python-weather-backend.git
cd python-weather-backend

# Create & activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Add your OpenWeather API key
echo "API_KEY=your_openweather_api_key" > .env

# Run server
uvicorn main:app --reload
