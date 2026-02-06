import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import FastAPI

try:
    cred = credentials.Certificate("credentials.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    firebase_status = "Conectado"
except Exception as e:
    db = None
    firebase_status = f"Error: {str(e)}"

app = FastAPI()


@app.get("/")
def read_root():
    return {
        "status": "API Online",
        "backend": "FastAPI + uv",
        "firebase_connection": firebase_status,
    }


@app.get("/test-write")
def test_write():
    if not db:
        return {"error": "No hay conexión a base de datos"}

    try:
        # Escribimos un dato de prueba
        ref = db.collection("test_collection").document("prueba_lautaro")
        ref.set(
            {
                "mensaje": "Si lees esto, Firestore funciona",
                "timestamp": firestore.SERVER_TIMESTAMP,
            }
        )

        # Lo leemos de vuelta para confirmar
        doc = ref.get()
        return {"resultado": "Éxito", "dato_guardado": doc.to_dict()}
    except Exception as e:
        return {"error": str(e)}
