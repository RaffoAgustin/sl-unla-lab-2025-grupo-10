from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from DataBase.models import Turno, Persona
from DataBase.database import get_db
from Utils.utils import validar_y_formatear_fecha_especial
from fastapi.responses import StreamingResponse

from borb.pdf import Document, Page, SingleColumnLayout, Paragraph, PDF, FixedColumnWidthTable as Table
from borb.pdf.canvas.color.color import HexColor
from borb.pdf.canvas.layout.layout_element import Alignment
from decimal import Decimal
from io import BytesIO

router = APIRouter()

# Obtener los turnos de una fecha
@router.get("/pdf/turnos-por-fecha")
def exportar_turnos_de_una_fecha_csv(fecha: str, db: Session = Depends(get_db)):
    try:
        fecha_formateada = validar_y_formatear_fecha_especial(fecha)
        turnos = db.query(Turno).join(Persona).filter(Turno.fecha == fecha_formateada).all()
                
        # Crear PDF
        doc = Document()
        page = Page()
        doc.add_page(page)
        layout = SingleColumnLayout(page)
        
        # Título
        layout.add(
            Paragraph(
                "Reporte de Turnos por Fecha",
                font="Helvetica-Bold",
                font_size=20,
                font_color=HexColor("#000000"),
                horizontal_alignment = Alignment.CENTERED))
        
        
        layout.add(Paragraph(f"Fecha: {fecha_formateada}", font_size=Decimal(13)))
        # layout.add(Paragraph(" "))
        
        if turnos:
            # Tabla
            tabla = Table(number_of_rows=len(turnos) + 1, number_of_columns=5)

            # Encabezados
            black = HexColor("#000000")
                
            # Encabezados
            tabla.add(Paragraph("Nombre", font="Helvetica-Bold", font_color=black, horizontal_alignment = Alignment.CENTERED))
            tabla.add(Paragraph("DNI", font="Helvetica-Bold", font_color=black, horizontal_alignment = Alignment.CENTERED))
            tabla.add(Paragraph("ID", font="Helvetica-Bold", font_color=black, horizontal_alignment = Alignment.CENTERED))
            tabla.add(Paragraph("Hora", font="Helvetica-Bold", font_color=black, horizontal_alignment = Alignment.CENTERED))
            tabla.add(Paragraph("Estado", font="Helvetica-Bold", font_color=black, horizontal_alignment = Alignment.CENTERED))
            
            # Filas
            for t in turnos:
                nombre = t.persona.nombre if t.persona else "Sin nombre"
                dni = t.persona.dni if t.persona else "-"
                hora = t.hora.strftime("%H:%M") if t.hora else "—"
                estado = t.estado if t.estado else "—"

                tabla.add(Paragraph(nombre, horizontal_alignment = Alignment.CENTERED))
                tabla.add(Paragraph(dni, horizontal_alignment = Alignment.CENTERED))
                tabla.add(Paragraph(str(t.id), horizontal_alignment = Alignment.CENTERED))
                tabla.add(Paragraph(hora, horizontal_alignment = Alignment.CENTERED))
                tabla.add(Paragraph(estado , horizontal_alignment = Alignment.CENTERED))

            layout.add(tabla)
                
        else:
            # Si no hay turnos en esa fecha
            return {"mensaje": f"No se encontraron turnos para la fecha {fecha_formateada}"}
        
        # Generar PDF en memoria
        buffer = BytesIO()
        PDF.dumps(buffer, doc)
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=turnos_{fecha_formateada}.pdf"}
        )
    
    except Exception as e: raise HTTPException(status_code=500, detail=f"Error al obtener los turnos de la fecha {fecha}: {str(e)}")