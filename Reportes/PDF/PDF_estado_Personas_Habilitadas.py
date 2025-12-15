from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from DataBase.database import get_db
from DataBase.models import Persona
from Utils.utils import calcular_edad

from fastapi.responses import StreamingResponse
from borb.pdf import Document, Page, SingleColumnLayout, Paragraph, PDF, FixedColumnWidthTable as Table
from borb.pdf.canvas.color.color import HexColor
from borb.pdf.canvas.layout.layout_element import Alignment
from io import BytesIO
from Utils.config import CONFIG_PDF_PERSONA

router = APIRouter()

@router.get("/pdf/estado-personas")
def exportar_estado_personas_pdf(
    habilitada: bool = Query(..., description="true o false"),
    db: Session = Depends(get_db)
):
    try:
        
        cfg = CONFIG_PDF_PERSONA

        # Consultar personas
        personas = db.query(Persona).filter(
            Persona.esta_habilitado == habilitada
        ).all()
        
        # Crear PDF
        doc = Document()
        
        if personas:

            # Dividir personas en grupos por página
            max_personas_por_pagina = cfg["max_rows"]
            total_paginas = (len(personas) + max_personas_por_pagina - 1) // max_personas_por_pagina #Division entera, no puede ser decimal
            

            for num_pagina in range(total_paginas): 
                
                #Agregar una nueva página en cada iteración
                page = Page(width=cfg["page_width"], height=cfg["page_height"])
                doc.add_page(page)
                layout = SingleColumnLayout(page)

                # Título (Solamente en la primera página)
                if num_pagina == 0:
                    layout.add(
                        Paragraph(
                            f"Personas {"habilitadas" if habilitada else "deshabilitadas"} para sacar turno",
                            font="Helvetica-Bold",
                            font_size=20,
                            font_color=HexColor("#000000"),
                            horizontal_alignment = Alignment.CENTERED))
                

                #Calibra la variable "Personas_pagina_actual" para que tenga un valor de inicio y fin, cambiando en cada iteración del bucle
                inicio = num_pagina * max_personas_por_pagina
                fin = min(inicio + max_personas_por_pagina, len(personas)) #Elige el menor entre limite de pagina o el total de personas
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
        
        else:
            return {"mensaje": f"No se encontraron personas {"habilitadas" if habilitada else "deshabilitadas"}"}

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
