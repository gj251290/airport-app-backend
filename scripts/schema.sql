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
  code TEXT NOT NULL UNIQUE,    
  name TEXT NOT NULL,
  country TEXT, 
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ===== 3) airports =====
CREATE TABLE IF NOT EXISTS airports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code TEXT NOT NULL UNIQUE,    
  name TEXT NOT NULL,
  city TEXT,
  country TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ===== 4) flights =====
CREATE TABLE IF NOT EXISTS flights (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  airline_id UUID NOT NULL REFERENCES airlines(id) ON DELETE RESTRICT,
  flight_number TEXT NOT NULL, 
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