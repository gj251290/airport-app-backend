# Plan de trabajo — Airport App (FastAPI + Neon + CLI por HTTP)

Entrega: **Domingo 8 de marzo**  
Enfoque: **vertical por entidad** (DB + modelo SQLAlchemy + schemas Pydantic + endpoints FastAPI + cliente HTTP CRUD + submenú CLI).  
Además, una persona integra routers + menú principal.

Repositorio: `Nicogrih/airport-app`  
Ramas: `dev`, `qa`, `prod`  
Estructura actual (actualizada):

```text
app/
  crud/        # cliente HTTP + menús CLI
  database/    # session async, base, engine
  endpoints/   # routers FastAPI
  models/      # modelos SQLAlchemy
  schemas/     # schemas Pydantic
  services/    # lógica de negocio (pricing, etc.)
  utils/       # helpers CLI, validaciones, formatos
  app.py       # servidor FastAPI (uvicorn app.app:app --reload)
  main.py      # menú CLI (python -m app.main)
docs/
```

---

## 1) Objetivo final del sistema (flujo completo)

### Backend (FastAPI)

- API REST con FastAPI + SQLAlchemy async + Neon PostgreSQL.
- Endpoints CRUD para:
  - `users`, `airlines`, `airports`, `flights`, `reservations`, `passengers`, `reservation_flights`.
- Swagger `/docs` debe mostrar los 7 recursos.

### CLI (consola, solo HTTP)

- No toca DB directamente.
- Consume la API por HTTP con `httpx`.
- Menú principal por entidades y submenús CRUD.
- Flujo guiado para reservas:
  1. elegir usuario
  2. crear reserva (HOLD)
  3. agregar vuelos (wizard: solo ida / ida y vuelta)
  4. agregar pasajeros
  5. confirmar reserva (CONFIRMED)

---

## 2) Base de datos (Neon) — `scripts/schema.sql`

> Ejecutar en Neon SQL Editor.  
> Requisito: `pgcrypto` para `gen_random_uuid()`.

```sql
-- airport-app
-- Neon PostgreSQL - UUID v4

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ===== 1) users =====
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT NOT NULL UNIQUE,
  full_name TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'CLIENT' CHECK (role IN ('CLIENT', 'ADMIN')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ===== 2) airlines =====
CREATE TABLE IF NOT EXISTS airlines (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code TEXT NOT NULL UNIQUE,     -- e.g. "AV"
  name TEXT NOT NULL,
  country TEXT NULL,             -- opcional
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ===== 3) airports =====
CREATE TABLE IF NOT EXISTS airports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code TEXT NOT NULL UNIQUE,     -- IATA e.g. "BOG"
  name TEXT NOT NULL,
  city TEXT NULL,                -- opcional
  country TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ===== 4) flights =====
CREATE TABLE IF NOT EXISTS flights (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  airline_id UUID NOT NULL REFERENCES airlines(id) ON DELETE RESTRICT,
  flight_number TEXT NOT NULL, -- e.g. "AV123"
  origin_airport_id UUID NOT NULL REFERENCES airports(id) ON DELETE RESTRICT,
  destination_airport_id UUID NOT NULL REFERENCES airports(id) ON DELETE RESTRICT,
  departure_at TIMESTAMPTZ NOT NULL,
  arrival_at TIMESTAMPTZ NOT NULL,
  status TEXT NOT NULL DEFAULT 'SCHEDULED'
    CHECK (status IN ('SCHEDULED', 'RESCHEDULED', 'CANCELED')),
  price_cop INTEGER NOT NULL DEFAULT 150000 CHECK (price_cop >= 0),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT chk_flights_airports_different CHECK (origin_airport_id <> destination_airport_id),
  CONSTRAINT chk_flights_time_order CHECK (arrival_at > departure_at),
  UNIQUE (airline_id, flight_number, departure_at)
);

CREATE INDEX IF NOT EXISTS idx_flights_origin_departure
  ON flights (origin_airport_id, departure_at);

CREATE INDEX IF NOT EXISTS idx_flights_destination_arrival
  ON flights (destination_airport_id, arrival_at);

-- ===== 5) reservations =====
CREATE TABLE IF NOT EXISTS reservations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  status TEXT NOT NULL DEFAULT 'HOLD'
    CHECK (status IN ('HOLD', 'CONFIRMED', 'CANCELED', 'EXPIRED')),
  total_amount_cop INTEGER NOT NULL DEFAULT 0 CHECK (total_amount_cop >= 0),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_reservations_user_created
  ON reservations (user_id, created_at DESC);

-- ===== 6) passengers =====
CREATE TABLE IF NOT EXISTS passengers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  reservation_id UUID NOT NULL REFERENCES reservations(id) ON DELETE CASCADE,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  document_number TEXT NOT NULL,
  birth_date DATE NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_passengers_reservation
  ON passengers (reservation_id);

-- ===== 7) reservation_flights =====
CREATE TABLE IF NOT EXISTS reservation_flights (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  reservation_id UUID NOT NULL REFERENCES reservations(id) ON DELETE CASCADE,
  flight_id UUID NOT NULL REFERENCES flights(id) ON DELETE RESTRICT,
  segment_order INTEGER NOT NULL CHECK (segment_order >= 1),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (reservation_id, flight_id),
  UNIQUE (reservation_id, segment_order)
);

CREATE INDEX IF NOT EXISTS idx_reservation_flights_reservation
  ON reservation_flights (reservation_id);

CREATE INDEX IF NOT EXISTS idx_reservation_flights_flight
  ON reservation_flights (flight_id);
```

---

## 3) Contrato de API (REST) — rutas obligatorias

### Recursos (7)

- `/api/users`
- `/api/airlines`
- `/api/airports`
- `/api/flights`
- `/api/reservations`
- `/api/passengers`
- `/api/reservation-flights`

### CRUD mínimo por recurso

Cada recurso debe tener:

- `GET /api/<resource>` (listar)
- `GET /api/<resource>/{id}` (obtener por id)
- `POST /api/<resource>` (crear)
- `PUT /api/<resource>/{id}` (actualizar) _(para reservation_flights puede omitirse si no se usa)_
- `DELETE /api/<resource>/{id}` (eliminar)

### Filtros recomendados (para CLI)

- `GET /api/passengers?reservation_id=<uuid>`
- `GET /api/reservation-flights?reservation_id=<uuid>`

---

## 4) Flujo completo CLI (lo que se va a demostrar)

### Paso A: Cargar catálogo

1. Aerolíneas: crear y listar.
2. Aeropuertos: crear y listar.
3. Vuelos: crear y listar (usando airline + airports).

### Paso B: Crear usuario

4. Usuarios: crear un `CLIENT`.

### Paso C: Reserva guiada (flujo de negocio)

5. Reservas -> Crear (wizard):
   - lista usuarios y eliges por número
   - crea reserva en `HOLD`
   - entra a “Gestionar reserva”
6. Gestionar reserva -> Agregar vuelos:
   - wizard: Solo ida / Ida y vuelta
   - eliges vuelo(s) por número (mostrando datos legibles)
7. Gestionar reserva -> Agregar pasajeros:
   - crea 1..N pasajeros
8. Gestionar reserva -> Confirmar reserva:
   - cambia status a `CONFIRMED`
   - valida: al menos 1 vuelo + 1 pasajero

---

## 5) Implementación (vertical) — backend + cli por entidad

### Reglas

- Modelos SQLAlchemy deben reflejar el schema de Neon (7 tablas).
- Schemas Pydantic deben incluir:
  - `Create`, `Update`, `Read`.
- Endpoints deben usar SQLAlchemy async con `AsyncSession`.
- CLI debe:
  - listar y elegir por número donde sea posible
  - evitar pedir UUID manual

---

## 6) Reparto por integraciones (solo 3 integrantes)

### Integrador + Reservas/Pasajeros (Gerardo Jiménez)

Responsable de:

**Integración**

- `app/app.py`: registrar routers de todos los endpoints.
- `app/crud/http_client.py`: cliente base consistente (soporta `params=`).
- `app/main.py`: menú principal (conecta submenús).
- Revisión final `.env`, README, ejecución.

**Vertical**

- `reservations` (endpoints + CLI flujo guiado)
- `passengers` (endpoints + CLI)
- `reservation_flights` (endpoints + CLI)
- `services/pricing.py` (recalcular total) + su integración en endpoints

### Integrante A: Catálogo (Airlines + Airports) (Nicolas Grijalba)

Entregables:

- `app/models/airlines.py`
- `app/models/airports.py`
- `app/schemas/airlines.py`
- `app/schemas/airports.py`
- `app/endpoints/airlines.py`
- `app/endpoints/airports.py`
- `app/crud/airlines.py`
- `app/crud/airports.py`
- `app/crud/menu_airlines.py`
- `app/crud/menu_airports.py`

### Integrante B: Users + Flights (Ángel Gutiérrez)

Entregables:

- `app/models/user.py`
- `app/models/flights.py`
- `app/schemas/users.py`
- `app/schemas/flights.py`
- `app/endpoints/users.py`
- `app/endpoints/flights.py`
- `app/crud/users.py`
- `app/crud/flights.py`
- `app/crud/menu_users.py`
- `app/crud/menu_flights.py`

---

## 7) Checklist final de entrega (demo)

- [ ] FastAPI corre: `uvicorn app.app:app --reload`
- [ ] Swagger muestra 7 tags y endpoints
- [ ] Neon conectado (operaciones CRUD reales)
- [ ] CRUD completo para 7 recursos _(reservation_flights puede no tener PUT)_
- [ ] CLI corre: `python -m app.main`
- [ ] CLI permite:
  - crear catálogo (airlines, airports, flights)
  - crear user
  - crear reserva con wizard
  - agregar vuelos con wizard (solo ida / ida-vuelta)
  - agregar pasajeros
  - confirmar reserva
  - ver total actualizado
- [ ] PEP8, tipos, docstrings básicos
- [ ] `.env` ignorado
- [ ] PRs: feature branches -> `dev`, luego `dev -> qa`, `qa -> prod`
