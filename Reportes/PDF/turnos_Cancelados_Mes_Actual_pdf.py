from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import extract
from datetime import date
from fastapi.responses import FileResponse
from pathlib import Path

from borb.pdf import Document, Page, SingleColumnLayout, Paragraph, PDF

from DataBase.database import get_db
from DataBase.models import Turno
from Utils.config import ESTADOS_TURNO, MESES

router = APIRouter()

@router.get("/pdf/turnos-cancelados-por-mes")
def exportar_turnos_cancelados_mes_actual_pdf(db: Session = Depends(get_db)):
    try:
        hoy = date.today()

        # Obtener turnos cancelados del mes actual
        turnos = db.query(Turno).filter(
            Turno.estado == ESTADOS_TURNO[1],
            extract('year', Turno.fecha) == hoy.year,
            extract('month', Turno.fecha) == hoy.month
        ).all()

        if not turnos:
            return {"mensaje": f"No hay turnos cancelados en {MESES[hoy.month - 1]} {hoy.year}"}

        pdf_path = Path(f"Reportes/PDF_Generados/turnos_cancelados_{hoy.year}_{hoy.month}.pdf")
        pdf_path.parent.mkdir(parents=True, exist_ok=True)

        doc = Document()
        page = Page()
        doc.append_page(page)
        layout = SingleColumnLayout(page)

        layout.append_layout_element(Paragraph(f"Turnos cancelados - {MESES[hoy.month - 1]} {hoy.year}"))

        for t in turnos:
            texto = f"ID: {t.id}, Persona ID: {t.persona_id}, Fecha: {t.fecha}, Hora: {t.hora}, Estado: {t.estado}"
            layout.append_layout_element(Paragraph(texto))

        PDF.write(what=doc, where_to=str(pdf_path))

        return FileResponse(
            path=str(pdf_path),
            media_type="application/pdf",
            filename=pdf_path.name
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar PDF: {str(e)}")

