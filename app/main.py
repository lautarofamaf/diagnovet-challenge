import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI, UploadFile, File, HTTPException
from app.extractor import extract_data_from_pdf

# --- 1. Configuración de Firebase (Singleton) ---
try:
    # Intenta cargar credenciales. Si falla, la API arranca pero sin DB.
    cred = credentials.Certificate("credentials.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    firebase_status = "Conectado"
except Exception as e:
    db = None
    firebase_status = f"Error de conexión: {str(e)}"

app = FastAPI(title="DiagnoVET API - Backend Challenge")


# --- 2. Endpoints de Salud (Health Checks) ---
@app.get("/")
def read_root():
    return {
        "status": "API Online",
        "backend": "FastAPI + uv",
        "firebase_connection": firebase_status,
        "mode": "Serverless Ready",
    }


# --- 3. El Endpoint Principal  ---
@app.post("/upload")
async def upload_report(file: UploadFile = File(...)):
    """
    Recibe un PDF, extrae datos + imágenes y guarda todo en Firestore.
    """
    # A. Validaciones previas
    if not db:
        raise HTTPException(status_code=503, detail="Base de datos no disponible")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF")

    try:
        # B. Lectura del archivo en Memoria RAM
        # Usamos await porque es una operación de entrada/salida
        content = await file.read()

        # C. Llamada al 'Cirujano' (Tu lógica de extracción)
        # Esto nos devuelve el diccionario con paciente, dueño e imágenes en base64
        extraction_result = extract_data_from_pdf(content)

        # D. Preparar el documento para la Base de Datos
        doc_data = {
            "filename": file.filename,
            "upload_timestamp": firestore.SERVER_TIMESTAMP,
            "processed": True,
            # Guardamos los datos estructurados (Paciente, Fecha, Diagnóstico)
            "data": extraction_result["structured_data"],
            # Guardamos las imágenes (Plan C: Base64 directo en DB)
            "images": extraction_result["images"],
            "image_count": extraction_result["image_count"],
        }

        # E. Guardar en Firestore (Colección 'reports')
        # .add() genera un ID automático y devuelve (timestamp, documento_ref)
        update_time, doc_ref = db.collection("reports").add(doc_data)

        # F. Respuesta al Cliente
        return {
            "status": "success",
            "message": "Reporte procesado exitosamente",
            "report_id": doc_ref.id,
            "extracted_preview": extraction_result["structured_data"],
            "images_found": extraction_result["image_count"],
        }

    except Exception as e:
        # Si algo explota (PDF corrupto, error de lógica), devolvemos error 500
        print(f"Error procesando upload: {e}")  # Log para ver en terminal
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


# --- 4. Endpoint de Debug (Opcional) ---
@app.get("/reports/{report_id}")
def get_report(report_id: str):
    """Permite ver un reporte guardado por su ID"""
    if not db:
        raise HTTPException(status_code=503, detail="Sin DB")

    doc = db.collection("reports").document(report_id).get()
    if doc.exists:
        return doc.to_dict()
    else:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
