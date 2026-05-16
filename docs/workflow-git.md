# Flujo de trabajo del equipo (Git)

## Ramas principales
- **main** → código estable y funcional.
- **dev** → copia exacta de `main`, usada para integrar features.
- **feature/...** → ramas individuales donde cada integrante desarrolla su parte.

---

## Cómo debe trabajar cada integrante

### 1. Partir siempre desde `dev`
```bash
git checkout dev
git pull
```

---

### 2. Crear una rama por feature (no por persona)
Ejemplo:
```bash
git checkout -b feature/vuelos
git checkout -b feature/usuarios
git checkout -b feature/reservas
```

Cada persona trabaja **solo** en su propia rama de feature.

---

### 3. Hacer commits normalmente dentro del feature
```bash
git add .
git commit -m "Implementar endpoint para listar vuelos"
```

---

### 4. Mantener el feature actualizado con `dev`
Cada cierto tiempo:
```bash
git checkout dev
git pull
git checkout feature/vuelos
git merge dev
```

Esto evita conflictos grandes al final.

---

### 5. Cuando el feature esté listo → Pull Request hacia `dev`
- Nunca se hace PR directo a `main`.
- `dev` es la rama donde se integran todos los features.
- Otro integrante revisa el código antes del merge.

---

### 6. Cuando varios features estén listos → merge de `dev` → `main`
Esto se hace solo cuando:
- `dev` está estable  
- todo funciona correctamente  
- no hay conflictos  

---

## Resumen rápido
- **main** = estable  
- **dev** = integración  
- **feature/...** = trabajo individual  
- Cada uno crea su feature desde `dev`  
- Se integran features a `dev` mediante PR  
- `main` solo recibe código probado  