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
from Utils.config import CONFIG_PDF_TURNOS

router = APIRouter()

# Obtener los turnos de una fecha
@router.get("/pdf/turnos-por-fecha")
def exportar_turnos_de_una_fecha_csv(fecha: str, db: Session = Depends(get_db)):
    try:
        fecha_formateada = validar_y_formatear_fecha_especial(fecha)
        turnos = db.query(Turno).join(Persona).filter(Turno.fecha == fecha_formateada).all()

        if not turnos:
            # Si no hay turnos en esa fecha
            return {"mensaje": f"No se encontraron turnos para la fecha {fecha_formateada}"}
                
        cfg = CONFIG_PDF_TURNOS

        # Cálculo inicial de cantidad de páginas
        max_turnos_por_pagina = cfg["max_rows"]
        total_paginas = (len(turnos) + max_turnos_por_pagina - 1) // max_turnos_por_pagina #Division entera, no puede ser decimal
   
        # Crear PDF
        doc = Document()
        
        #Bucle de páginas
        for num_pagina in range(total_paginas):               
            
            #Agrego una nueva pagina en cada bucle
            page = Page(width=cfg["page_width"], height=cfg["page_height"])
            doc.add_page(page)
            layout = SingleColumnLayout(page)

            # Título
            if num_pagina == 0:
                layout.add(
                    Paragraph(
                        f"Reporte de Turnos en {fecha_formateada}",
                        font="Helvetica-Bold",
                        font_size=20,
                        font_color=HexColor("#000000"),
                        horizontal_alignment = Alignment.CENTERED))
        
            #Calibra la variable "Turnos_pagina_actual" para que tenga un valor de inicio y fin, cambiando en cada iteración del bucle
            inicio = num_pagina * max_turnos_por_pagina
            fin = min(inicio + max_turnos_por_pagina, len(turnos)) #Elige entre limite de pagina o el total de turnos
            turnos_pagina_actual = turnos[inicio:fin] #Toma solo los elementos desde el inicio hasta el fin

            # Tabla
            tabla = Table(
                number_of_rows=len(turnos_pagina_actual) + 1, #Numero de filas
                number_of_columns=len(cfg["column_widths"]), #Numero de columnas (Sacado del env)
                column_widths=cfg["column_widths"]) #Ancho de columnas (Sacado del env)

            # Encabezados
            headers = cfg["column_header_name"] #Tomo los nombres de los encabezados del env
            for h in headers:
                tabla.add(Paragraph(h, font="Helvetica-Bold", horizontal_alignment=Alignment.CENTERED))
    
            # Filas
            for t in turnos_pagina_actual:
                datos=[
                    str(t.id),
                    str(t.persona_id) if t.persona_id else "-",
                    t.fecha.strftime("%d/%m/%Y") if t.fecha else "-",
                    t.hora.strftime("%H:%M") if t.hora else "—",
                    t.estado if t.estado else "—"
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
            headers={"Content-Disposition": f"attachment; filename=turnos_{fecha_formateada}.pdf"}
        )
    
    except Exception as e: raise HTTPException(status_code=500, detail=f"Error al obtener los turnos de la fecha {fecha}: {str(e)}")