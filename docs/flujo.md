# Flujo completo del programa (CLI) – Airport App

Este documento describe el **flujo ideal completo** del programa en consola, de principio a fin, pensando en un usuario “normal” (no técnico).  
La idea es que el CLI guíe el orden lógico de creación de datos y de compra (reserva), evitando pedir UUIDs cuando se pueda elegir de listas.

---

## 0) Inicio del programa

1. El usuario ejecuta el CLI.
2. El CLI crea un `APIClient` con `API_BASE_URL` (por defecto `http://127.0.0.1:8000`).
3. Muestra:

**MENÚ PRINCIPAL**

- 1. Aerolíneas
- 2. Aeropuertos
- 3. Vuelos
- 4. Usuarios
- 5. Reservas
- 0. Salir

---

## 1) Aerolíneas (Airlines)

Objetivo: crear el catálogo de aerolíneas.

### Menú Aerolíneas

- 1. Listar aerolíneas
- 2. Ver aerolínea (por ID)
- 3. Crear aerolínea
- 4. Actualizar aerolínea
- 5. Eliminar aerolínea
- 0. Volver

### Flujo recomendado (mínimo para poder crear vuelos)

1. Crear aerolínea (ej. Avianca, LATAM, American Airlines).
2. Listar para verificar.

Resultado: existen `airlines` disponibles para usar en `flights`.

---

## 2) Aeropuertos (Airports)

Objetivo: crear catálogo de aeropuertos.

### Menú Aeropuertos

- 1. Listar aeropuertos
- 2. Ver aeropuerto
- 3. Crear aeropuerto
- 4. Actualizar aeropuerto
- 5. Eliminar aeropuerto
- 0. Volver

### Flujo recomendado

1. Crear aeropuertos con `code` (BOG, MDE, CLO, MIA, JFK, etc).
2. Listar para verificar.

Resultado: existen `airports` disponibles para usar como origen/destino en `flights`.

---

## 3) Vuelos (Flights)

Objetivo: crear vuelos que se puedan reservar.

### Menú Vuelos

- 1. Listar vuelos
- 2. Ver vuelo
- 3. Crear vuelo
- 4. Actualizar vuelo
- 5. Eliminar vuelo
- 0. Volver

### Flujo recomendado

1. Crear vuelo:
   - Elegir aerolínea (desde lista de aerolíneas)
   - Elegir aeropuerto origen (desde lista de aeropuertos)
   - Elegir aeropuerto destino (desde lista de aeropuertos)
   - Ingresar `flight_number`
   - Ingresar fecha/hora salida y llegada
   - Estado (SCHEDULED, etc.)
2. Listar vuelos y verificar.

Resultado: existen vuelos para seleccionar en el proceso de reserva.

---

## 4) Usuarios (Users)

Objetivo: crear usuarios que “compran” o gestionan reservas.

### Menú Usuarios

- 1. Listar
- 2. Ver uno
- 3. Crear
- 4. Actualizar
- 5. Eliminar
- 0. Volver

### Flujo recomendado

1. Crear usuario (email, full_name, role).
2. Listar para verificar.

Resultado: existe por lo menos un usuario con rol CLIENT para poder crear una reserva.

---

## 5) Reservas (Reservations) – Flujo “de negocio”

Este es el flujo principal tipo compra:

**Reserva = contenedor** (cabecera)  
Dentro de la reserva se agregan:

- Vuelos (itinerario) ✅ (tabla intermedia “reservation_flights”)
- Pasajeros ✅ (“passengers” con reservation_id)

### Menú Reservas (ideal)

- 1. Listar reservas
- 2. Ver reserva (cabecera)
- 3. Crear reserva (asistente guiado)
- 4. Actualizar reserva (estado / total)
- 5. Eliminar reserva
- 6. Gestionar reserva (vuelos y pasajeros)
- 0. Volver

---

# 5.1) Asistente: Crear reserva (GUIADO)

**Objetivo:** que el usuario no tenga que pegar UUIDs.

### Paso 1: Seleccionar usuario comprador

- El CLI lista usuarios (por email y nombre)
- El usuario elige por número (1,2,3…)

Resultado: se obtiene `user_id`.

### Paso 2: Crear la reserva (cabecera)

- Se crea con:
  - `status = HOLD` (por defecto)
  - `total_amount_cop = 0` (temporal)
  - `user_id` seleccionado

Resultado: se obtiene `reservation_id`.

### Paso 3: Entrar automáticamente a “Gestionar reserva”

Después de crear, el CLI debe entrar directo al submenú para:

1. Agregar vuelos
2. Agregar pasajeros

---

# 5.2) Submenú: Gestionar reserva

Este es el corazón del flujo.

### Menú “Gestionar reserva”

- 1. Ver vuelos de la reserva
- 2. Agregar vuelos (asistente de viaje)
- 3. Eliminar vuelo de la reserva
- 4. Ver pasajeros de la reserva
- 5. Agregar pasajero
- 6. Eliminar pasajero
- 7. Confirmar reserva (opcional pero recomendado)
- 0. Volver

---

## 5.2.1) Ver vuelos de la reserva

- Si no hay vuelos asociados: mostrar mensaje claro:
  - “La reserva aún no tiene vuelos asociados.”
- Si hay vuelos:
  - listarlos en orden (segment_order / tramo)
  - mostrar datos legibles (flight_number, airline, origen/destino, salida/llegada, estado)

---

## 5.2.2) Agregar vuelos (asistente “tipo de viaje”)

En vez de pedir “segment_order” se usa un wizard.

### Wizard: Tipo de viaje

- 1. Solo ida
- 2. Ida y vuelta
- 0. Cancelar

#### Solo ida

1. El CLI lista vuelos disponibles con información amigable:
   - `flight_number | airline | ORG->DST | dep->arr | status`
2. Usuario elige por número.
3. Se agrega como “tramo 1”.

#### Ida y vuelta

1. Elegir vuelo de ida → se agrega como tramo 1
2. Elegir vuelo de vuelta → se agrega como tramo 2

Regla:

- El usuario nunca escribe UUID (solo elige número).

---

## 5.2.3) Ver pasajeros de la reserva

- Si no hay pasajeros: mensaje claro:
  - “La reserva aún no tiene pasajeros.”
- Si hay:
  - listarlos (nombre, documento, fecha nacimiento, etc.)

---

## 5.2.4) Agregar pasajero

1. Capturar datos:
   - nombre, apellido, documento, nacimiento (opcional)
2. Crear passenger con `reservation_id` (automático, no lo escribe el usuario)
3. Mostrar el pasajero creado.

---

## 5.2.5) Confirmar reserva (cierre de compra)

Recomendado como opción directa del menú.

- Cambia `status` a `CONFIRMED`.

Validaciones recomendadas:

- Debe existir al menos 1 vuelo asociado a la reserva
- Debe existir al menos 1 pasajero

Si no se cumple:

- Mensaje: “No puedes confirmar: faltan vuelos/pasajeros.”

---

# 6) Dependencias de backend (importante)

Para que el flujo funcione completo, el backend debe exponer:

## Entidades base

- `/api/users`
- `/api/airlines`
- `/api/airports`
- `/api/flights`
- `/api/reservations`
- `/api/passengers` (idealmente con `?reservation_id=...`)

## Relación reserva-vuelos (obligatorio para itinerario)

Debe existir algo como:

- `POST /api/reservation-flights`
- `GET /api/reservation-flights?reservation_id=...`
- `DELETE /api/reservation-flights/{id}`

Sin esto:

- el CLI puede crear reservas y pasajeros, pero NO puede asociar vuelos a la reserva.

---

# 7) Resumen del “orden correcto” para demo

1. Crear aerolíneas
2. Crear aeropuertos
3. Crear vuelos
4. Crear usuario
5. Crear reserva
6. Agregar vuelo(s) a la reserva (ida / ida-vuelta)
7. Agregar pasajeros
8. Confirmar reserva
