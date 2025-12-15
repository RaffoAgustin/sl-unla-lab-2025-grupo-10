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
from io import BytesIO
from Utils.config import CONFIG_PDF_PERSONA

router = APIRouter()

@router.get("/pdf/turnos-cancelados-minimo")
def exportar_personas_con_turnos_cancelados_pdf(
    min_turnos: int = Query(..., description="Minimo de turnos cancelados"), #Pide al usuario el mínimo de Turnos cancelados (... significa obligatorio)
    db: Session = Depends(get_db)  #Inyecta automáticamente una sesión de base de datos
):
    try:
        if min_turnos <= 0:
                raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El valor minimo no puede ser negativo o 0"
        )

        cfg = CONFIG_PDF_PERSONA

        personas=(
                db.query(Persona) #Hace una consulta de personas
                .join(Turno) #Junto a sus turnos
                .filter(Turno.estado == ESTADOS_TURNO.Cancelado) #Tomo unicamente a los turnos cancelados
                .group_by(Persona.id) #Agrupo a las personas según su id, necesario para que las func funcionen correctamente
                .having(func.count(Turno.id) >= min_turnos) #Filtro los grupos (cada persona) donde la cantidad de turnos (ya filtrados) sean mayores al minimo
                .all() #Muestro todas las personas con estas condiciones
            )
        
        # Crear PDF
        doc = Document()
        
        #Validación de seguridad
        if not personas:
            return {"mensaje": f"No se encontraron personas con mas de {min_turnos} turnos cancelados"}
            
        # Cálculo inicial de cantidad de páginas
        max_personas_por_pagina = cfg["max_rows"]
        total_paginas = (len(personas) + max_personas_por_pagina - 1) // max_personas_por_pagina #Division entera, no puede ser decimal
        
        #Bucle de páginas
        for num_pagina in range(total_paginas):
            
            page = Page(width=cfg["page_width"], height=cfg["page_height"])
            doc.add_page(page)
            layout = SingleColumnLayout(page)

            # Título
            if num_pagina == 0:
                layout.add(
                    Paragraph(
                        f"Personas con {min_turnos} o más turnos cancelados",
                        font="Helvetica-Bold",
                        font_size=20,
                        font_color=HexColor("#000000"),
                        horizontal_alignment = Alignment.CENTERED))

            #Calibra la variable "Personas_pagina_actual" para que tenga un valor de inicio y fin, cambiando en cada iteración del bucle
            inicio = num_pagina * max_personas_por_pagina
            fin = min(inicio + max_personas_por_pagina, len(personas)) #Elige entre limite de pagina o el total de personas
            personas_pagina_actual = personas[inicio:fin] #Toma solo los elementos desde el inicio hasta el fin

            # Tabla
            tabla = Table(
                number_of_rows=len(personas_pagina_actual) + 1,
                number_of_columns=len(cfg["column_widths"]),
                column_widths=cfg["column_widths"])

            # Encabezados
            headers = cfg["column_header_name"] #Tomo los nombres de los encabezados del env
            for h in headers:
                tabla.add(Paragraph(h, font="Helvetica-Bold", horizontal_alignment=Alignment.CENTERED))
    
            # Filas de datos
            for p in personas_pagina_actual:
                datos = [
                    str(p.id),
                    p.nombre if p.nombre else "Sin nombre",
                    p.email if p.email else "-",
                    p.dni if p.dni else "-",
                    p.telefono if p.telefono else "-",
                    p.fecha_nacimiento.strftime("%d/%m/%Y") if p.fecha_nacimiento else "-",
                    str(calcular_edad(p.fecha_nacimiento)) if p.fecha_nacimiento else "-",
                    "Sí" if p.esta_habilitado else "No"
                ]
                
                for dato in datos:
                    tabla.add(Paragraph(
                        dato, 
                        horizontal_alignment=Alignment.LEFT, 
                        respect_newlines_in_text=True))

            layout.add(tabla)
            
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