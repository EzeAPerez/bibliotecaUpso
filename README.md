# Proyecto Biblioteca UPSO - API Obras

API desarrollada con **FastAPI**.

---

## Requisitos

* Python 3.10 o superior

---

## Instalación y ejecución

### 1. Crear entorno virtual

```bash
py -m venv .venv
```

---

### 2. Activar entorno virtual

**Windows (PowerShell):**

```bash
.venv\Scripts\activate
```

**Windows (CMD):**

```bash
.venv\Scripts\activate.bat
```

**Linux / Mac:**

```bash
source .venv/bin/activate
```

---

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

### 4. Ejecutar la aplicación

Ir a la carpeta `app`:

```bash
cd app
```

Levantar el servidor:

```bash
uvicorn main:app --reload
```

---

## Acceso a la API

Una vez iniciada:

* API: http://127.0.0.1:8000
* Documentación Swagger: http://127.0.0.1:8000/docs
