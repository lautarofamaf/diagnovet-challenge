import fitz  # PyMuPDF
import base64
import re
from typing import Dict, Any, List


def extract_data_from_pdf(pdf_bytes: bytes) -> Dict[str, Any]:
    """
    Abre el PDF en memoria, extrae texto con layout y saca las imágenes.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text = ""
    images_data = []

    # 1. Iteramos por las páginas
    for page_num, page in enumerate(doc):
        # A. Texto: Usamos "text" para mantener el orden natural de lectura
        full_text += page.get_text("text") + "\n"

        # B. Imágenes: Extracción a bajo nivel
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            try:
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]

                # Filtro: Ignorar imágenes muy chicas (iconos, logos, firmas)
                if len(image_bytes) < 5000:
                    continue

                # Convertir a Base64
                img_b64 = base64.b64encode(image_bytes).decode("utf-8")

                images_data.append(
                    {
                        "page": page_num + 1,
                        "type": base_image["ext"],
                        "data_base64": img_b64,
                    }
                )
            except Exception as e:
                print(f"Error extrayendo imagen {img_index}: {e}")

    doc.close()

    # 2. Parseo Inteligente de Texto
    structured_data = parse_veterinary_report(full_text)

    return {
        "raw_text_preview": full_text[:500] + "...",  # Solo para debug
        "structured_data": structured_data,
        "images": images_data,
        "image_count": len(images_data),
    }


def parse_veterinary_report(text: str) -> Dict[str, str]:
    """
    Aplica Regex diseñados para informes veterinarios típicos (Español).
    """
    data = {
        "patient": "Desconocido",
        "owner": "Desconocido",
        "date": "No encontrada",
        "report_type": "Informe General",
        "diagnosis": "Sin conclusiones específicas",
    }

    # --- 1. Paciente / Mascota ---
    # Busca "Paciente:" o "Mascota:" seguido de cualquier cosa hasta el fin de linea
    patient_match = re.search(
        r"(?:Paciente|Mascota|Nombre):\s*(.*?)(?:\n|$)", text, re.IGNORECASE
    )
    if patient_match:
        data["patient"] = patient_match.group(1).strip()

    # --- 2. Propietario / Tutor ---
    owner_match = re.search(
        r"(?:Propietario|Tutor|Dueño|Solicitante):\s*(.*?)(?:\n|$)", text, re.IGNORECASE
    )
    if owner_match:
        data["owner"] = owner_match.group(1).strip()

    # --- 3. Fecha ---
    # Busca formatos DD/MM/AAAA o DD-MM-AAAA
    date_match = re.search(r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})", text)
    if date_match:
        data["date"] = date_match.group(1)

    # --- 4. Tipo de Estudio (Basado en título) ---
    if "ecografia" in text.lower() or "ecográfico" in text.lower():
        data["report_type"] = "Ecografía"
    elif "radiografia" in text.lower() or "radiológico" in text.lower():
        data["report_type"] = "Radiografía"
    elif "cardiologico" in text.lower() or "ecocardiograma" in text.lower():
        data["report_type"] = "Ecocardiograma"

    # --- 5. Diagnóstico / Conclusiones (Multilínea) ---
    # Estrategia: Buscar la palabra "Conclusión" o "Diagnóstico" y tomar todo
    # hasta que aparezca otra palabra clave fuerte (como "Firma" o fin de archivo).

    # Patrón: (Conclusión/Diagnostico/Impresión) ... (texto) ... (Fin o Firma)
    diagnosis_pattern = r"(?:Conclusi[oó]n|Diagn[oó]stico|Impresi[oó]n|Hallazgos):\s*(.*?)(?:\n\s*(?:Firma|Dr\.|M\.V\.|Atentamente)|$)"

    diag_match = re.search(diagnosis_pattern, text, re.IGNORECASE | re.DOTALL)
    if diag_match:
        # Limpiamos saltos de línea excesivos
        raw_diag = diag_match.group(1).strip()
        clean_diag = re.sub(
            r"\s+", " ", raw_diag
        )  # Reemplaza multiples espacios/enters por uno solo
        data["diagnosis"] = clean_diag[
            :500
        ]  # Limitamos a 500 caracteres para no romper la DB

    return data
