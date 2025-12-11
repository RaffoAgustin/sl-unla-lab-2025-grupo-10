from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from Utils.config import ESTADOS_TURNO
from DataBase.models import Turno, Persona
from DataBase.database import get_db
from Utils.utils import calcular_edad
from fastapi.responses import StreamingResponse
from borb.pdf import Document, Page, SingleColumnLayout, Paragraph, PDF, FixedColumnWidthTable as Table
from borb.pdf.canvas.color.color import HexColor
from borb.pdf.canvas.layout.layout_element import Alignment
from decimal import Decimal
from io import BytesIO

router = APIRouter()

@router.get("/pdf/turnos-cancelados-minimo")
def exportar_personas_con_turnos_cancelados_pdf(
    min: int = Query(..., description="Minimo de turnos cancelados"), #Pide al usuario el mínimo de Turnos cancelados (... significa obligatorio)
    db: Session = Depends(get_db)  #Inyecta automáticamente una sesión de base de datos
):
    try:
        if min <= 0:
                raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El valor minimo no puede ser negativo o 0"
        )

        # Crear PDF
        doc = Document()
        page = Page()
        doc.add_page(page)
        layout = SingleColumnLayout(page)
        
        # Título
        layout.add(
            Paragraph(
                f"Reporte de Turnos Cancelados con un mínimo de {min}",
                font="Helvetica-Bold",
                font_size=20,
                font_color=HexColor("#000000"),
                horizontal_alignment = Alignment.CENTERED))
        
        personas=(
                db.query(Persona) #Hace una consulta de personas
                .join(Turno) #Junto a sus turnos
                .filter(Turno.estado == ESTADOS_TURNO.Cancelado) #Tomo unicamente a los turnos cancelados
                .group_by(Persona.id) #Agrupo a las personas según su id, necesario para que las func funcionen correctamente
                .having(func.count(Turno.id) >= min) #Filtro los grupos (cada persona) donde la cantidad de turnos (ya filtrados) sean mayores al minimo
                .all() #Muestro todas las personas con estas condiciones
            )

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
            return {"mensaje": f"No se encontraron personas con mas de {min} turnos cancelados"}
        
        # Generar PDF en memoria
        buffer = BytesIO()
        PDF.dumps(buffer, doc)
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=turnos_cancelados_min_{min}.pdf"}
        )
            
    except Exception as e:
        print("Error en el reporte de turnos cancelados:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error Inesperado al obtener el reporte"
        )