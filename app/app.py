import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.endpoints.users import router as users_router
from app.endpoints.airlines import router as airlines_router
from app.endpoints.airports import router as airports_router
from app.endpoints.flights import router as flights_router
from app.endpoints.reservations import router as reservations_router
from app.endpoints.passengers import router as passengers_router
from app.endpoints.reservation_flights import router as reservation_flights_router
from app.endpoints.auth import router as auth_router

# exceptions y handlers
from app.core.handlers import register_error_handlers
from app.core.security import get_current_user

load_dotenv()


def _cors_origins() -> list[str]:
    raw = os.getenv(
        "CORS_ALLOW_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173,http://localhost:8080,http://127.0.0.1:8080",
    )
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


app = FastAPI(title="airport-app", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

# manejadores de excepciones
register_error_handlers(app)

protected_dependencies = [Depends(get_current_user)]

app.include_router(auth_router)
app.include_router(users_router, dependencies=protected_dependencies)
app.include_router(airlines_router, dependencies=protected_dependencies)
app.include_router(airports_router, dependencies=protected_dependencies)
app.include_router(flights_router, dependencies=protected_dependencies)
app.include_router(reservations_router, dependencies=protected_dependencies)
app.include_router(passengers_router, dependencies=protected_dependencies)
app.include_router(reservation_flights_router, dependencies=protected_dependencies)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
