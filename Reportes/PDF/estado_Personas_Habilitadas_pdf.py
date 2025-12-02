from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from DataBase.database import get_db
from DataBase.models import Persona
from Utils.utils import calcular_edad

from fastapi.responses import StreamingResponse
from borb.pdf import Document, Page, SingleColumnLayout, Paragraph, PDF, FixedColumnWidthTable as Table
from borb.pdf.canvas.color.color import HexColor
from borb.pdf.canvas.layout.layout_element import Alignment
from decimal import Decimal
from io import BytesIO

router = APIRouter()

@router.get("/pdf/estado-personas")
def exportar_estado_personas_pdf(
    habilitada: bool = Query(..., description="true o false"),
    db: Session = Depends(get_db)
):
    try:
        # Consultar personas
        personas = db.query(Persona).filter(
            Persona.esta_habilitado == habilitada
        ).all()
        
        # Crear PDF
        doc = Document()
        page = Page()
        doc.add_page(page)
        layout = SingleColumnLayout(page)
        
        # Título
        layout.add(
            Paragraph(
                "Reporte de Estado de Personas Habilitadas",
                font="Helvetica-Bold",
                font_size=20,
                font_color=HexColor("#000000"),
                horizontal_alignment = Alignment.CENTERED))
        
        layout.add(Paragraph(f"Habilitadas: {habilitada}", font_size=Decimal(13)))
        # layout.add(Paragraph(" "))
        
        if personas:
            # Tabla
            tabla = Table(
                number_of_rows=len(personas) + 1,
                number_of_columns=8,
                column_widths=[
                    Decimal(40),  # ID
                    Decimal(70), # Nombre
                    Decimal(200), # Email
                    Decimal(90),  # DNI
                    Decimal(110),  # Teléfono
                    Decimal(100), # Fecha nacimiento
                    Decimal(55),  # Edad
                    Decimal(85),  # Habilitada
                ])

            # Encabezados
            black = HexColor("#000000")
                
            # Encabezados
            tabla.add(Paragraph("ID", font="Helvetica-Bold", font_color=black, horizontal_alignment = Alignment.CENTERED))
            tabla.add(Paragraph("Nombre", font="Helvetica-Bold", font_color=black, horizontal_alignment = Alignment.CENTERED))
            tabla.add(Paragraph("Email", font="Helvetica-Bold", font_color=black, horizontal_alignment = Alignment.CENTERED))
            tabla.add(Paragraph("DNI", font="Helvetica-Bold", font_color=black, horizontal_alignment = Alignment.CENTERED))
            tabla.add(Paragraph("Teléfono", font="Helvetica-Bold", font_color=black, horizontal_alignment = Alignment.CENTERED))
            tabla.add(Paragraph("Fecha de nacimiento", font="Helvetica-Bold", font_color=black, horizontal_alignment = Alignment.CENTERED))
            tabla.add(Paragraph("Edad", font="Helvetica-Bold", font_color=black, horizontal_alignment = Alignment.CENTERED))
            tabla.add(Paragraph("Habilitada", font="Helvetica-Bold", font_color=black, horizontal_alignment = Alignment.CENTERED))

            # Filas
            for p in personas:
                nombre = p.nombre if p.nombre else "Sin nombre"
                email = p.email if p.email else "-"
                dni = p.dni if p.dni else "-"
                telefono = p.telefono if p.telefono else "-"
                fecha_nacimiento = (
                    p.fecha_nacimiento.strftime("%d/%m/%Y")
                    if p.fecha_nacimiento 
                    else "-")
                edad = calcular_edad(p.fecha_nacimiento) if p.fecha_nacimiento else "-"
                edad = str(edad)
                habilitado = "Sí" if p.esta_habilitado else "No"

                tabla.add(Paragraph(str(p.id), horizontal_alignment = Alignment.CENTERED))
                tabla.add(Paragraph(nombre, horizontal_alignment = Alignment.CENTERED))
                tabla.add(Paragraph(email, horizontal_alignment = Alignment.CENTERED))
                tabla.add(Paragraph(dni, horizontal_alignment = Alignment.CENTERED))
                tabla.add(Paragraph(telefono , horizontal_alignment = Alignment.CENTERED))
                tabla.add(Paragraph(fecha_nacimiento , horizontal_alignment = Alignment.CENTERED))
                tabla.add(Paragraph(edad , horizontal_alignment = Alignment.CENTERED))
                tabla.add(Paragraph(habilitado , horizontal_alignment = Alignment.CENTERED))

            layout.add(tabla)
        
        else:
            return {"mensaje": f"No se encontraron personas con habilitada={habilitada}"}

        # Generar PDF en memoria
        buffer = BytesIO()
        PDF.dumps(buffer, doc)
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=estado_personas_{habilitada}.pdf"}
        )
        
    except Exception as e:
        print("Error en /pdf/estado-personas:", str(e))
        raise HTTPException(status_code=500, detail="Error interno del servidor")
