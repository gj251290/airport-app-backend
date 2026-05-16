import pytest
import uuid
from datetime import datetime, timedelta
from pydantic import ValidationError

# Importamos tus modelos y schemas
from app.models.user import User
from app.models.flights import Flight
from app.models.airlines import Airline
from app.schemas.users import UserCreate  # Para probar validación de entrada


@pytest.mark.asyncio
async def test_user_schema_validation():
    """
    PRUEBA: Validar que el Schema de User detecte errores de formato.
    Esto asegura que la API no acepte basura.
    """
    # 1. Caso exitoso
    user_data = {
        "email": "gerardo@example.com",
        "password": "Gerardo123!",
        "full_name": "Gerardo Jimenez",
        "role": "CLIENT",
    }
    user_schema = UserCreate(**user_data)
    assert user_schema.email == "gerardo@example.com"

    # 2. Caso fallido: Email inválido (Pydantic debe lanzar ValidationError)
    with pytest.raises(ValidationError):
        UserCreate(
            email="esto-no-es-un-email",
            password="Gerardo123!",
            full_name="Test",
            role="CLIENT",
        )


@pytest.mark.asyncio
async def test_create_user_model_logic():
    """Validar que el modelo de base de datos acepta los campos correctamente."""
    user_id = uuid.uuid4()
    new_user = User(
        id=user_id,
        email=f"test_{user_id.hex[:6]}@example.com",
        password_hash="fake_hash_for_test",
        full_name="Gerardo Test",
        role="CLIENT",
    )
    assert new_user.full_name == "Gerardo Test"
    assert new_user.role == "CLIENT"


@pytest.mark.asyncio
async def test_flight_constraints_logic():
    """Validar restricciones de lógica en vuelos."""
    departure = datetime.now()
    arrival = departure + timedelta(hours=2)

    flight = Flight(
        airline_id=uuid.uuid4(),
        flight_number="AV123",
        origin_airport_id=uuid.uuid4(),
        destination_airport_id=uuid.uuid4(),
        departure_at=departure,
        arrival_at=arrival,
        price_cop=250000,
        status="SCHEDULED",
    )

    assert flight.origin_airport_id != flight.destination_airport_id
    assert flight.arrival_at > flight.departure_at
    assert flight.status == "SCHEDULED"


@pytest.mark.asyncio
async def test_airline_logic():
    """Validar que el modelo Airline se comporta según lo esperado."""
    airline = Airline(code="AVA", name="Avianca", country="Colombia")
    assert len(airline.code) <= 10
    assert airline.name == "Avianca"
