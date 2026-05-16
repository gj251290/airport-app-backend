# Plan de Trabajo - Entrega Final (11 de Abril)

## 1. Objetivo y Equipo

Implementar los requisitos del examen 2, distribuyendo las tareas de forma equitativa entre los tres integrantes del equipo:

- **Ángel David Gutiérrez Ladino**
- **Gerardo Andrés Jiménez Piedrahíta**
- **Nicolás Josué Grijalba Huertas**

## 2. Pipeline

El pipeline de CI/CD (con GitHub Actions). Las acciones se ejecutan en "runners" que son máquinas virtuales (normalmente basadas en Linux) que se crean solo para ejecutar el pipeline.

**La clave es:**

- **Estandarizar:** El archivo `requirements.txt` asegura que todos (y el pipeline) usen las mismas versiones de las librerías.
- **Scripts Agnósticos:** Los comandos en el archivo YML deben ser compatibles con el entorno del runner (ej. `python -m pip install -r requirements.txt` funciona en ambos).
- **Variables de Entorno:** La base de datos se conecta usando secretos (secrets) de GitHub, no con un archivo `.env` local.

Si el pipeline se ejecuta correctamente en GitHub, significa que la configuración del proyecto es portable y no depende del Windows local.

## 3. División de Tareas por Integrante

Para optimizar el tiempo, las tareas se dividen en tres grandes bloques que pueden trabajarse en paralelo.

---

### **Tarea Principal 1: Base de Datos: Migraciones y Seeder**

- **Responsable:** Ángel David Gutiérrez Ladino
- **Rama Git:** `feat/db-migrations-seeder`

El objetivo es reemplazar la creación manual de tablas (`schema.sql`) por un sistema de migraciones automatizado y un poblado inicial de datos (seeder).

**Pasos detallados:**

1.  **Investigar e Instalar Alembic:** Alembic es el estándar para migraciones con SQLAlchemy.
    - Añadir `alembic` al archivo `requirements.txt`.
    - Instalarlo: `pip install alembic`.
    - Inicializar Alembic en el proyecto: `alembic init alembic`. Esto creará una carpeta `alembic/` y un archivo `alembic.ini`.

2.  **Configurar Alembic:**
    - En `alembic/env.py`, importar los modelos de `app/models` y configurar el `target_metadata`.
    - En `alembic.ini`, configurar la URL de la base de datos para que la lea desde las variables de entorno (similar a como ya lo hacen).

3.  **Crear la Primera Migración:**
    - Generar automáticamente la migración inicial basada en los modelos existentes: `alembic revision --autogenerate -m "Crear tablas iniciales"`.
    - Revisar el archivo de migración generado en `alembic/versions/`. Este archivo contiene el código Python para crear todas las tablas.

4.  **Crear el Script Seeder (`seeder.py`):**

    # Plan de Trabajo - Examen 2

    ## 1. Objetivo

    Entregar el proyecto del Examen 2 (sin incluir el video). Este plan aplica la distribución vertical (cada integrante desarrolla una vertical completa) para asegurar carga de trabajo equivalente y aprendizaje práctico.

    ## 2. Principio de distribución
    - Todos implementan una vertical completa: modelos, esquemas, endpoints, CRUD, pruebas unitarias y CLI para su entidad.
    - Única excepción: Gerardo (Integrador) también implementa JWT y CORS y coordina CI/CD.
    - Migraciones y `seeder` son colaborativos: cada quien genera las migraciones para sus cambios y añade sus datos seed en `app/database/seeder.py`. El Integrador ejecuta las migraciones en CI.

    ## 3. Asignación por persona (verticales)

    ### Nicolás Josué Grijalba Huertas — responsabilidades principales:
    - `alembic.ini`
    - `alembic/env.py`
    - `alembic/README`
    - `alembic/script.py.mako`
    - `alembic/versions/53c3ac11e09c_migracion_inicial.py`
    - `alembic/versions/a7f3d4c92b10_add_password_hash_to_users.py`
    - `app/crud/airlines.py`
    - `app/crud/airports.py`
    - `app/crud/menu_airlines.py`
    - `app/crud/menu_airports.py`
    - `app/endpoints/airlines.py`
    - `app/endpoints/airports.py`
    - `app/models/airlines.py`
    - `app/models/airports.py`
    - `app/schemas/airlines.py`
    - `app/schemas/airports.py`
    - `requirements.txt`

    ### Ángel David Gutiérrez Ladino — Users + Flights, responsabilidades principales:
    - `app/crud/auth.py`
    - `app/crud/flights.py`
    - `app/crud/http_client.py`
    - `app/crud/menu_flights.py`
    - `app/crud/menu_users.py`
    - `app/crud/users.py`
    - `app/endpoints/auth.py`
    - `app/endpoints/flights.py`
    - `app/endpoints/users.py`
    - `app/models/flights.py`
    - `app/models/user.py`
    - `app/schemas/auth.py`
    - `app/schemas/flights.py`
    - `app/schemas/users.py`
    - `tests/test_api_logic.py`

    ### Gerardo Andrés Jiménez Piedrahíta — Integrador, responsabilidades principales:
    - `.github/workflows/ci-cd-pipeline.yml`
    - `README.md`
    - `app/app.py`
    - `app/core/exceptions.py`
    - `app/core/handlers.py`
    - `app/core/security.py`
    - `app/crud/menu_reservations.py`
    - `app/crud/passengers.py`
    - `app/crud/reservation_flights.py`
    - `app/crud/reservations.py`
    - `app/database/base.py`
    - `app/database/seeder.py`
    - `app/database/session.py`
    - `app/endpoints/passengers.py`
    - `app/endpoints/reservation_flights.py`
    - `app/endpoints/reservations.py`
    - `app/main.py`
    - `app/models/passengers.py`
    - `app/models/reservation_flights.py`
    - `app/models/reservations.py`
    - `app/schemas/passengers.py`
    - `app/schemas/reservation_flights.py`
    - `app/schemas/reservations.py`
    - `app/services/pricing.py`
    - `app/utils/cli_utils.py`

## 4. Reglas de trabajo (breve)

- Cada integrante crea un único branch feature para subir su parte: `feat/<task>` (task en inglés).
- Branch por integrante (usar exactamente estos nombres al crear la rama):
  - Gerardo: `feat/booking-engine-and-cicd`
  - Ángel: `feat/auth-and-flight-services`
  - Nicolás: `feat/infrastructure-and-catalogs`
- Reglas de nomenclatura: minúsculas, usar guiones (`-`), sin espacios.
- Empuja la rama y abre un PR hacia `dev`. El Integrador (`Gerardo`) hará merge después de que CI pase y haya al menos una aprobación.
- Si se cambian los modelos, se debe genera una migración de Alembic (`alembic revision --autogenerate`) y se añade los seeds a `app/database/seeder.py`.
