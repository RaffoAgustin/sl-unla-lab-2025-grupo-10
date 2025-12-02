from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from DataBase.models import Turno, Persona
from DataBase.database import get_db
from Utils.utils import validar_dni
from fastapi.responses import StreamingResponse

from borb.pdf import Document, Page, SingleColumnLayout, Paragraph, PDF, FixedColumnWidthTable as Table
from borb.pdf.canvas.color.color import HexColor
from borb.pdf.canvas.layout.layout_element import Alignment
from decimal import Decimal
from io import BytesIO

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
                
        # Crear PDF
        doc = Document()
        page = Page()
        doc.add_page(page)
        layout = SingleColumnLayout(page)
        
        # Título
        layout.add(
            Paragraph(
                "Reporte de Turnos por Persona",
                font="Helvetica-Bold",
                font_size=20,
                font_color=HexColor("#000000"),
                horizontal_alignment = Alignment.CENTERED))
        
        
        layout.add(Paragraph(f"Usuario: {turnos[0].persona.nombre}", font_size=Decimal(13)))
        # layout.add(Paragraph(" "))
        
        if turnos:
            # Tabla
            tabla = Table(number_of_rows=len(turnos) + 1, number_of_columns=4)

            # Encabezados
            black = HexColor("#000000")
                
            # Encabezados
            tabla.add(Paragraph("ID", font="Helvetica-Bold", font_color=black, horizontal_alignment = Alignment.CENTERED))
            tabla.add(Paragraph("Fecha", font="Helvetica-Bold", font_color=black, horizontal_alignment = Alignment.CENTERED))
            tabla.add(Paragraph("Hora", font="Helvetica-Bold", font_color=black, horizontal_alignment = Alignment.CENTERED))
            tabla.add(Paragraph("Estado", font="Helvetica-Bold", font_color=black, horizontal_alignment = Alignment.CENTERED))
            
            # Filas
            for t in turnos:
                fecha = t.fecha.strftime("%d/%m/%Y")
                hora = t.hora.strftime("%H:%M") if t.hora else "—"
                estado = t.estado if t.estado else "—"

                tabla.add(Paragraph(str(t.id), horizontal_alignment = Alignment.CENTERED))
                tabla.add(Paragraph(fecha, horizontal_alignment = Alignment.CENTERED))
                tabla.add(Paragraph(hora, horizontal_alignment = Alignment.CENTERED))
                tabla.add(Paragraph(estado, horizontal_alignment = Alignment.CENTERED))

            layout.add(tabla)
                
        else:
            # Si esa persona no tiene turnos
            return {"mensaje": f"La persona con DNI {dni} no tiene turnos asignados"}
        
        # Generar PDF en memoria
        buffer = BytesIO()
        PDF.dumps(buffer, doc)
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=turnos_{turnos[0].persona.nombre}.pdf"}
        )
    
    except Exception as e: raise HTTPException(status_code=500, detail=f"Error al obtener los turnos de la persona con DNI {dni}: {str(e)}")