# Python Weather Backend
[12112025] - Update
Insert instructions on how to activate in Windows and bypass PowerShell protection in Visual Studio Code

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

# Create virtual environment
python -m venv .venv

# -------------------------------
# Linux / Mac
# -------------------------------
source .venv/bin/activate

# -------------------------------
# Windows (PowerShell in VS Code)
# -------------------------------

# 1. Allow running local scripts (only once)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 2. If you are already inside a venv and get activation errors
deactivate

# 3. (Optional) Delete existing venv if broken
rmdir .venv /s /q

# 4. Create new virtual environment
python -m venv .venv

# 5. Activate virtual environment
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Add your WeatherAPI key
# Create a .env file in the root folder with:
# WEATHER_API_KEY=your_weatherapi_key

# Run server
uvicorn main:app --reload

