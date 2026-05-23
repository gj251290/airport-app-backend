# airport-app

Proyecto académico para un sistema de reservas de vuelos.

- **Backend:** Python + FastAPI
- **Servidor:** Uvicorn
- **Base de datos:** Neon (PostgreSQL)
- **ORM/Driver:** SQLAlchemy (async) + asyncpg
- **Menú por consola:** CRUD consumiendo la API por HTTP (httpx)
- **Equipo:** 3 personas (Windows + VS Code)
- **Convenciones:** commits en **español**, código/estructuras en **inglés**.

---

## Integrantes

- Ángel David Gutiérrez Ladino
- Gerardo Andrés Jiménez Piedrahíta
- Nicolás Josué Grijalba Huertas

---

## Entidades y contrato de API

Entidades (CRUD):

- `auth` → `/api/auth/login` (JWT)
- `users` → `/api/users`
- `reservations` → `/api/reservations`
- `airlines` → `/api/airlines`
- `airports` → `/api/airports`
- `flights` → `/api/flights`
- `passengers` → `/api/passengers`
- `reservation_flights` → `/api/reservation-flights`

> Todas las rutas están bajo el prefijo `/api/...`.

---

## Estructura del repositorio

```text
airport-app/
├── .github/
│   └── workflows/
│       └── ci-cd-pipeline.yml      # Pipeline de CI/CD (Black, Ruff, Tests)
├── alembic/                        # Configuración de migraciones
│   ├── versions/                   # Historial de cambios en la base de datos
│   └── env.py                      # Configuración del entorno de Alembic
├── app/
│   ├── core/                       # Lógica central del sistema
│   │   ├── exceptions.py           # Definición de excepciones personalizadas
│   │   └── handlers.py             # Manejadores de errores
│   │   └── security.py             # JWT y hashing de passwords
│   ├── crud/                       # Lógica de acceso a datos (Create, Read, Update, Delete)
│   │   ├── auth.py
│   │   ├── airlines.py
│   │   ├── airports.py
│   │   ├── flights.py
│   │   ├── http_client.py
│   │   ├── menu_airlines.py
│   │   ├── menu_airports.py
│   │   ├── menu_flights.py
│   │   ├── menu_reservations.py
│   │   ├── menu_users.py
│   │   ├── passengers.py
│   │   ├── reservation_flights.py
│   │   ├── reservations.py
│   │   └── users.py
│   ├── database/                   # Configuración de la conexión a la BD
│   │   ├── base.py                 # Declarative base para modelos
│   │   ├── seeder.py               # Inserción de datos iniciales
│   │   └── session.py              # Gestión de sesiones (SQLAlchemy)
│   ├── endpoints/                  # Rutas de la API (Controllers)
│   │   ├── auth.py
│   │   ├── airlines.py
│   │   ├── airports.py
│   │   ├── flights.py
│   │   ├── passengers.py
│   │   ├── reservation_flights.py
│   │   ├── reservations.py
│   │   └── users.py
│   ├── models/                     # Modelos de SQLAlchemy (Tablas)
│   │   ├── __init__.py
│   │   ├── airlines.py
│   │   ├── airports.py
│   │   ├── flights.py
│   │   ├── passengers.py
│   │   ├── reservation_flights.py
│   │   ├── reservations.py
│   │   └── user.py
│   ├── schemas/                    # Modelos de Pydantic (Validación de datos)
│   │   ├── auth.py
│   │   ├── airlines.py
│   │   ├── airports.py
│   │   ├── flights.py
│   │   ├── passengers.py
│   │   ├── reservation_flights.py
│   │   ├── reservations.py
│   │   └── users.py
│   ├── services/                   # Lógica de negocio compleja
│   │   └── pricing.py              # Cálculo de precios y tarifas
│   ├── utils/                      # Funciones de ayuda
│   │   └── cli_utils.py            # Utilidades para la interfaz de comandos
│   ├── __init__.py
│   ├── app.py                      # Configuración de la aplicación
│   └── main.py                     # Punto de entrada principal
├── scripts/
│   └── schema.sql                  # Script SQL inicial de la base de datos
├── tests/                          # Pruebas unitarias de lógica
│   └── __init__.py
│   └── test_api_logic.py
├── .gitignore
├── alembic.ini                     # Archivo de configuración de Alembic
├── requirements.txt                # Dependencias (FastAPI, SQLAlchemy, Ruff, etc.)
└── README.md
```

---

## Requisitos

- Python **3.11+** (probado en 3.11 y 3.14.4)
- Git
- VS Code
- Cuenta y base de datos en **Neon** (PostgreSQL)

---

## Configuración inicial (Windows)

### 1) Clonar el repositorio

```bash
git clone https://github.com/gj251290/airport-app-backend.git
cd airport-app
```

### 2) Crear y activar el entorno virtual

```bash
py -m venv .venv
# Si tienes varias versiones instaladas, especifica la que vas a usar:
# py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> Si PowerShell bloquea la activación, usa Command Prompt (cmd): `.venv\Scripts\activate.bat`

### 3) Instalar dependencias

El archivo `requirements.txt` ahora incluye las herramientas de desarrollo como `Alembic`, `Ruff`, `Black` y `Pytest`.

```bash
pip install -r requirements.txt
```

### 4) Configurar variables de entorno (`.env`)

Crea un archivo `.env` en la raíz del proyecto. Este archivo es local y **no se sube al repositorio**.

```env
# URL de conexión a tu base de datos de Neon
# Puedes usar la URL directa de Neon; el proyecto limpia sslmode/channel_binding.
DATABASE_URL=postgresql://USER:PASSWORD@HOST/DBNAME?sslmode=require

# Clave secreta para firmar JWT (obligatoria)
JWT_SECRET_KEY=REEMPLAZAR_POR_UNA_CLAVE_LARGA_Y_SEGURA

# Expiración del access token en minutos
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# Orígenes permitidos para CORS (separados por coma)
CORS_ALLOW_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Base URL para el CLI (opcional)
API_BASE_URL=http://127.0.0.1:8000
```

---

## Base de Datos (Alembic y Seeder)

Este proyecto utiliza **Alembic** para manejar las migraciones del esquema de la base de datos y un **seeder** para poblar datos iniciales. Ya no se usan scripts SQL manuales.

### 1) Aplicar Migraciones

Este comando actualiza el esquema de tu base de datos a la última versión según los modelos de SQLAlchemy.

```bash
alembic upgrade head
```

### 2) Poblar Datos Iniciales (Seeder)

Este comando ejecuta el script que inserta datos iniciales (catálogos, usuarios por defecto, etc.) de forma idempotente.

```bash
python -m app.database.seeder
```

---

## Ejecutar la API (modo desarrollo)

Con el entorno virtual activado:

```bash
uvicorn app.app:app --reload
```

- **Swagger:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

---

## Despliegue del backend (producción)

El backend ya está desplegado en Vercel y disponible en:

- **Base URL:** https://airport-app-backend.vercel.app/

Si el despliegue está activo, puedes consultar también la documentación en:

- **Swagger:** https://airport-app-backend.vercel.app/docs
- **ReDoc:** https://airport-app-backend.vercel.app/redoc

---

## Autenticación JWT (Bearer)

La API usa autenticación JWT para las rutas de negocio (`/api/users`, `/api/reservations`, etc.).

### 1) Login

Endpoint:

```text
POST /api/auth/login
```

Se envía `username` (email) y `password` como formulario (`application/x-www-form-urlencoded`).

Respuesta:

```json
{
  "access_token": "...",
  "token_type": "bearer",
  "expires_in_seconds": 3600
}
```

### 2) Uso del token

Enviar el token en la cabecera:

```text
Authorization: Bearer <access_token>
```

### 3) Usuarios de ejemplo del seeder

- `admin@admin.com` / `Admin123!`
- `gjimenez@gmail.com` / `Gerardo123!`
- `angelgutierrez@correo.com` / `Angel123!`

---

## Política CORS

Se configuró CORS en FastAPI con:

- Orígenes explícitos leídos desde `CORS_ALLOW_ORIGINS`.
- `allow_credentials=True`.
- Métodos permitidos: `GET, POST, PUT, PATCH, DELETE, OPTIONS`.
- Cabeceras permitidas: `Authorization, Content-Type, Accept`.

Para producción, define solo los dominios reales del frontend en `CORS_ALLOW_ORIGINS`.

---

## Pipeline de Integración Continua (CI/CD)

Este proyecto incluye un pipeline de CI/CD configurado en `.github/workflows/ci-cd-pipeline.yml`.

**¿Qué hace?**
Cada vez que se integra código en la rama `dev`, el pipeline se ejecuta automáticamente para:

1.  **Verificar la calidad del código** (linting y formato) con Ruff y Black.
2.  **Instalar las dependencias** para asegurar que el proyecto no tenga paquetes rotos.
3.  **Ejecutar las migraciones de la base de datos** con Alembic.
4.  **Poblar la base de datos** con datos iniciales usando el seeder.

El workflow solo se dispara en `push` y `pull_request` hacia `dev` (no se dispara en `qa` ni `prod`).

Esto garantiza que la rama `dev` siempre se mantenga estable y funcional.

**Secrets requeridos en GitHub Actions:**

- `DATABASE_URL`
- `JWT_SECRET_KEY`

---

## Ejecutar el menú por consola (CRUD por HTTP)

El menú **consume la API** mediante llamadas HTTP (no accede directo a la base de datos).

Al iniciar el CLI, primero solicita login y obtiene un JWT para consumir rutas protegidas.

1. Primero levanta el servidor:
   ```bash
   uvicorn app.app:app --reload
   ```
2. En otra terminal, ejecuta el menú:
   ```bash
   python -m app.main
   ```

---

## Flujo funcional (demo / caso de uso)

Flujo recomendado para demostrar el sistema:

1. Crear **aerolíneas**
2. Crear **aeropuertos**
3. Crear **vuelos** (usando airline + airports)
4. Crear **usuarios**
5. Crear **reserva**
6. Asociar **vuelos** a la reserva (tabla intermedia `reservation_flights`)
7. Agregar **pasajeros**
8. Confirmar la reserva

> Nota: el total de la reserva se calcula en backend (servicio `app/services/pricing.py`) según vuelos y cantidad de pasajeros.

---

## Flujo de trabajo con Git y GitHub

Ramas principales: `dev` (desarrollo), `qa` (pruebas), `prod` (producción).

1.  **Crear una rama por tarea desde `dev`**:
    ```bash
    git checkout dev
    git pull
    git checkout -b feat/nombre-tarea
    ```
2.  **Hacer commits en español**:
    ```bash
    git add .
    git commit -m "Describe el cambio en español"
    git push -u origin feat/nombre-tarea
    ```
3.  **Abrir Pull Request (PR) hacia `dev`**:
    - Al abrir el PR, el pipeline de CI/CD se ejecutará para verificar tu código.
    - El equipo debe revisar el código antes de aprobar.
4.  **Integrar a `dev`**: Una vez aprobado y con el pipeline en verde, haz merge del PR.
5.  **Promover a `qa` y `prod`**: Cuando `dev` esté estable, se crean PRs de `dev -> qa` y luego `qa -> prod`.

Regla clave: **todo cambio entra por PR**.

---

## Licencia

Este proyecto se distribuye bajo la **Licencia MIT**.

**Copyright (c) 2026 - Ángel Gutiérrez, Gerardo Jiménez, Nicolás Grijalba.**

Se otorga permiso por la presente, de forma gratuita, a cualquier persona que obtenga una copia de este software y de los archivos de documentación asociados, para utilizar el Software con fines estrictamente académicos, incluyendo sin limitación los derechos de usar, copiar, modificar, fusionar y publicar copias del Software, sujeto a las siguientes condiciones:

1. El aviso de copyright anterior y este aviso de permiso se incluirán en todas las copias o partes sustanciales del Software.
2. **EL SOFTWARE SE PROPORCIONA "TAL CUAL", SIN GARANTÍA DE NINGÚN TIPO, EXPRESA O IMPLÍCITA.**
3. El uso de este software es para fines de aprendizaje en el curso de Aplicación y Servicios Web 2026-1.
