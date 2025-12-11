from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import extract
from datetime import date
from DataBase.database import get_db
from DataBase.models import Turno
from Utils.config import ESTADOS_TURNO, MESES
from fastapi.responses import StreamingResponse
from borb.pdf import Document, Page, SingleColumnLayout, Paragraph, PDF, FixedColumnWidthTable as Table
from borb.pdf.canvas.color.color import HexColor
from borb.pdf.canvas.layout.layout_element import Alignment
from decimal import Decimal
from io import BytesIO

router = APIRouter()

@router.get("/pdf/turnos-cancelados-por-mes")
def exportar_turnos_cancelados_mes_actual_pdf(db: Session = Depends(get_db)):
    try:
        hoy = date.today()

        # Obtener turnos cancelados del mes actual
        turnos = db.query(Turno).filter(
            Turno.estado == ESTADOS_TURNO.Cancelado,
            extract('year', Turno.fecha) == hoy.year,
            extract('month', Turno.fecha) == hoy.month
        ).all()
        
        # Crear PDF
        doc = Document()
        page = Page()
        doc.add_page(page)
        layout = SingleColumnLayout(page)
        
        # Título
        layout.add(
            Paragraph(
                "Reporte de Turnos Cancelados en el Mes Actual",
                font="Helvetica-Bold",
                font_size=20,
                font_color=HexColor("#000000"),
                horizontal_alignment = Alignment.CENTERED))
        
        
        if turnos:
            # Tabla
            tabla = Table(number_of_rows=len(turnos) + 1, number_of_columns=5)

            # Encabezados
            black = HexColor("#000000")
                
            # Encabezados
            tabla.add(Paragraph("ID", font="Helvetica-Bold", font_color=black, horizontal_alignment = Alignment.CENTERED))
            tabla.add(Paragraph("Persona ID", font="Helvetica-Bold", font_color=black, horizontal_alignment = Alignment.CENTERED))
            tabla.add(Paragraph("Fecha", font="Helvetica-Bold", font_color=black, horizontal_alignment = Alignment.CENTERED))
            tabla.add(Paragraph("Hora", font="Helvetica-Bold", font_color=black, horizontal_alignment = Alignment.CENTERED))
            tabla.add(Paragraph("Estado", font="Helvetica-Bold", font_color=black, horizontal_alignment = Alignment.CENTERED))
            
            # Filas
            for t in turnos:
                persona_id = t.persona_id if t.persona_id else "-"
                fecha = (t.fecha.strftime("%d/%m/%Y") if t.fecha else "-")
                hora = (t.hora.strftime("%H:%M") if t.hora else "—")
                estado = t.estado if t.estado else "—"

                tabla.add(Paragraph(str(t.id), horizontal_alignment = Alignment.CENTERED))
                tabla.add(Paragraph(str(persona_id), horizontal_alignment = Alignment.CENTERED))
                tabla.add(Paragraph(fecha, horizontal_alignment = Alignment.CENTERED))
                tabla.add(Paragraph(hora, horizontal_alignment = Alignment.CENTERED))
                tabla.add(Paragraph(estado , horizontal_alignment = Alignment.CENTERED))

            layout.add(tabla)

        else:
            return {"mensaje": f"No hay turnos cancelados en {MESES[hoy.month - 1]} {hoy.year}"}

        # Generar PDF en memoria
        buffer = BytesIO()
        PDF.dumps(buffer, doc)
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=turnos_cancelados_{hoy.year}_{hoy.month}.pdf"})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar PDF: {str(e)}")

