from fastapi import FastAPI
from api.routes.weather import router as weather_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(weather_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)