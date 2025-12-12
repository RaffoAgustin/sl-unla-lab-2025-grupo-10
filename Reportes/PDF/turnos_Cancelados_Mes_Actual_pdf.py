from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import extract
from datetime import date
from DataBase.database import get_db
from DataBase.models import Turno
from Utils.config import ESTADOS_TURNO, MESES, CONFIG_PDF_TURNOS
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

        cfg = CONFIG_PDF_TURNOS

        hoy = date.today()

        # Obtener turnos cancelados del mes actual
        turnos = db.query(Turno).filter(
            Turno.estado == ESTADOS_TURNO.Cancelado,
            extract('year', Turno.fecha) == hoy.year,
            extract('month', Turno.fecha) == hoy.month
        ).all()
        
        if not turnos:
            return {"mensaje": f"No hay turnos cancelados en {MESES[hoy.month - 1]} {hoy.year}"}
        
        # Cálculo inicial de cantidad de páginas
        max_turnos_por_pagina = cfg["max_rows"]
        total_paginas = (len(turnos) + max_turnos_por_pagina - 1) // max_turnos_por_pagina #Division entera, no puede ser decimal
   
        # Crear PDF
        doc = Document()

        #Bucle de páginas
        for num_pagina in range(total_paginas):

            page = Page(width=cfg["page_width"], height=cfg["page_height"])
            doc.add_page(page)
            layout = SingleColumnLayout(page)
            
            # Título
            if num_pagina == 0:
                layout.add(
                    Paragraph(
                        f"Turnos Cancelados en {MESES[hoy.month - 1]} {hoy.year}",
                        font="Helvetica-Bold",
                        font_size=20,
                        font_color=HexColor("#000000"),
                        horizontal_alignment = Alignment.CENTERED))
            

            #Calibra la variable "Personas_pagina_actual" para que tenga un valor de inicio y fin, cambiando en cada iteración del bucle
            inicio = num_pagina * max_turnos_por_pagina
            fin = min(inicio + max_turnos_por_pagina, len(turnos)) #Elige entre limite de pagina o el total de personas
            turnos_pagina_actual = turnos[inicio:fin]

            
            # Tabla
            tabla = Table(
                number_of_rows=len(turnos_pagina_actual) + 1,
                number_of_columns=len(cfg["column_widths"]),
                column_widths=cfg["column_widths"])

            # Encabezados
            black = HexColor("#000000")
                
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
            headers={"Content-Disposition": f"attachment; filename=turnos_cancelados_{hoy.year}_{hoy.month}.pdf"})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar PDF: {str(e)}")

