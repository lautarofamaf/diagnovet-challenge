# 🐾 DiagnoVET API

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=flat&logo=fastapi)
![Google Cloud Firestore](https://img.shields.io/badge/Database-Firestore-orange?style=flat&logo=firebase)
![Render](https://img.shields.io/badge/Deploy-Render-black?style=flat&logo=render)

**Backend Engineering Challenge.**
Microservicio diseñado para el procesamiento automatizado de informes veterinarios en formato PDF. Extrae información clave (metadatos de pacientes, diagnósticos e imágenes médicas) y sincroniza los datos estructurados con la nube.

## 🚀 Tecnologías

* **Lenguaje:** Python 3.11
* **API Framework:** FastAPI (Asynchronous)
* **Base de Datos:** Google Cloud Firestore (NoSQL)
* **Procesamiento PDF:** PyMuPDF + Motor de Regex Personalizado
* **Infraestructura:** Docker + Render (CI/CD)
* **Gestión de Paquetes:** `uv` (Astral)

## 🏗️ Arquitectura del Sistema

El flujo de datos sigue un pipeline de tres etapas:

1.  **Ingesta (REST):** Endpoint `POST /upload` que acepta *streams* de archivos binarios (PDF).
2.  **Motor de Procesamiento:**
    * **Extracción de Texto:** Parseo de layout mediante PyMuPDF.
    * **Heurística de Datos:** Algoritmos basados en expresiones regulares (Regex) para identificar entidades (Dueño, Paciente, Fecha, Tipo de estudio).
    * **Extracción de Media:** Identificación y conversión de gráficos embebidos (Radiografías/Ecografías) a Base64*.
3.  **Persistencia:** Almacenamiento no relacional en Firestore para consultas en tiempo real.

> **Nota de Diseño:** *Actualmente las imágenes se almacenan como cadenas Base64 dentro del documento para simplificar la arquitectura del desafío. En un entorno de producción de alto volumen, se recomienda utilizar Google Cloud Storage y referenciar mediante URLs.*

## 🛠️ Instalación y Desarrollo Local

### Prerrequisitos
* Python 3.11+
* [uv](https://github.com/astral-sh/uv) (Gestor de proyectos recomendado)

### Pasos

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/lautarofamaf/diagnovet-challenge.git
    cd diagnovet-challenge
    ```

2.  **Instalar dependencias**
    ```bash
    uv sync
    ```

3.  **Configuración de Credenciales:**
    * Obtén tu archivo de cuenta de servicio de Firebase (`credentials.json`).
    * Colócalo en la **raíz** del proyecto.
    * *Nota: Este archivo está ignorado por git para seguridad.*

4.  **Ejecutar el servidor:**
    ```bash
    uv run uvicorn app.main:app --reload
    ```

## ☁️ Despliegue (Deploy)

El servicio está contenerizado mediante **Docker**. El `Dockerfile` multi-stage está optimizado para instalar dependencias del sistema (`libffi-dev`, `build-essential`) necesarias para el procesamiento de imágenes y PDFs antes de instalar las librerías de Python.

**Estado:** Activo en Render.com
**URL Base:** `https://diagnovet-api-lautaro.onrender.com`

### Endpoints Principales

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `GET` | `/` | Health Check. Retorna estado del servicio. |
| `POST` | `/upload` | **Core.** Recibe un PDF (`multipart/form-data`) y retorna el JSON estructurado. |
| `GET` | `/docs` | Documentación interactiva (Swagger UI). |

## Seguridad

* **Credenciales:** Las llaves de servicio (`credentials.json`) están excluidas del control de versiones (`.gitignore`) para evitar filtraciones.
* **Producción:** En el entorno de despliegue (Render), las credenciales se inyectan de forma segura utilizando "Secret Files".

---

*Developed by Lautaro for the Backend Engineering Challenge.*

```

```
