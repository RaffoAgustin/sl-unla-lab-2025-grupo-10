from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from DataBase.models import Turno, Persona
from DataBase.database import get_db
from Utils.utils import validar_dni
import pandas as pd
from fastapi.responses import FileResponse
from pathlib import Path
from borb.pdf import Document, Page, SingleColumnLayout, Paragraph, PDF

router = APIRouter()

# Obtener los turnos de una persona
@router.get("/pdf/turnos-por-persona")
def exportar_turnos_por_persona_csv(
    dni: str = Query(..., description="DNI de 8 dígitos"),
    db: Session = Depends(get_db)
):
    try:
        validar_dni(dni)
        turnos = db.query(Turno).join(Persona).filter(
            Turno.persona_id == Persona.id,
            Persona.dni == dni
        ).all()

        # Si esa persona no tiene turnos:
        if not turnos:
            return {"mensaje": f"No se encontraron turnos para la persona con DNI = {dni}"}
        
        # Crear carpeta si no existe
        pdf_path = Path(f"Reportes/PDF_Generados/turnos_por_persona{turnos[0].persona.nombre}.pdf")
        pdf_path.parent.mkdir(parents=True, exist_ok=True)

        # Crear PDF
        doc = Document()
        page = Page()
        doc.append_page(page)
        layout = SingleColumnLayout(page)

        # Título
        layout.append_layout_element(Paragraph(f"Turnos de la persona {turnos[0].persona.nombre}"))

        # Agregar cada turno como párrafo
        for t in turnos:
            texto = (
                f"ID Turno: {t.id}, "
                f"Fecha: {t.fecha.strftime("%d/%m/%Y")}, "
                f"Hora: {t.hora.strftime("%H:%M")}, "
                f"Estado: {t.estado}")
            
            layout.append_layout_element(Paragraph(texto))
        
        # Guardar PDF
        PDF.write(what=doc, where_to=str(pdf_path))

        # Devolver PDF
        return FileResponse(
            path=str(pdf_path),
            media_type="application/pdf",
            filename=pdf_path.name)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los turnos de la persona con DNI = {dni}: {str(e)}"
        )
