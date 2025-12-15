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
from Utils.config import CONFIG_PDF_TURNOS

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

        if not turnos:
            # Si esa persona no tiene turnos
            return {"mensaje": f"La persona con DNI {dni} no tiene turnos asignados"}
                
        cfg = CONFIG_PDF_TURNOS

        # Cálculo inicial de cantidad de páginas
        max_turnos_por_pagina = cfg["max_rows"]
        total_paginas = (len(turnos) + max_turnos_por_pagina - 1) // max_turnos_por_pagina #Division entera, no puede ser decimal
   
        # Crear PDF
        doc = Document()


        for num_pagina in range(total_paginas):
            
            #Agrego una nueva pagina en cada bucle
            page = Page(width=cfg["page_width"], height=cfg["page_height"])
            doc.add_page(page)
            layout = SingleColumnLayout(page)
        
        # Título
            if num_pagina == 0:
                layout.add(
                    Paragraph(
                        "Reporte de Turnos por Persona",
                        font="Helvetica-Bold",
                        font_size=20,
                        font_color=HexColor("#000000"),
                        horizontal_alignment = Alignment.CENTERED))
                
                layout.add(Paragraph(f"Usuario: {turnos[0].persona.nombre}", font_size=Decimal(13)))
        
        
            #Calibra la variable "Turnos_pagina_actual" para que tenga un valor de inicio y fin, cambiando en cada iteración del bucle
            inicio = num_pagina * max_turnos_por_pagina
            fin = min(inicio + max_turnos_por_pagina, len(turnos))  #Elige el menor entre limite de pagina o el total de turnos
            turnos_pagina_actual = turnos[inicio:fin] #Toma solo los elementos desde el inicio hasta el fin
        
            #Excluyo a persona_ID de la tabla, ya que es muy redundante
            idx_personaid = cfg["column_header_name"].index("Persona_ID") #Tomo el índice donde el Column_header_name es "Persona_ID"
            column_widths_filtrados = [w for i, w in enumerate(cfg["column_widths"]) if i != idx_personaid] #Por cada ancho de columna, toma el valor de todos salvo el que tenga el índice excluido 
                                                    #    ^  enumerate asocia un índice al vector, aunque tenga el mismo valor
            # Tabla
            tabla = Table(
                number_of_rows=len(turnos_pagina_actual) + 1, #Numero de filas
                number_of_columns=len(column_widths_filtrados), #Numero de columnas (Con persona_id excluido)
                column_widths=column_widths_filtrados) #Ancho de columnas (Con persona_id excluido)

            # Encabezados
            headers = cfg["column_header_name"] #Tomo los nombres de los encabezados del env
            # Para este endpoint, quitamos Persona_ID
            headers_filtrados = [h for h in headers if h != "Persona_ID"]
            
            for h in headers_filtrados:
                tabla.add(Paragraph(h, font="Helvetica-Bold", horizontal_alignment=Alignment.CENTERED))
    
    
            # Filas
            for t in turnos_pagina_actual:
                datos=[
                    str(t.id),
                    # str(t.persona_id) if t.persona_id else "-",
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
            headers={"Content-Disposition": f"attachment; filename=turnos_{turnos[0].persona.nombre}.pdf"}
        )
    
    except Exception as e: raise HTTPException(status_code=500, detail=f"Error al obtener los turnos de la persona con DNI {dni}: {str(e)}")