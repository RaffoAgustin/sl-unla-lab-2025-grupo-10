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
from borb.pdf.page.page_size import PageSize

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
        
        if personas:

            # Dividir personas en grupos por página
            max_personas_por_pagina = 20 #Variable de entorno por favor
            total_paginas = (len(personas) + max_personas_por_pagina - 1) // max_personas_por_pagina #Division entera, no puede ser decimal
            

            for num_pagina in range(total_paginas): 
                
                #Agregar una nueva página en cada iteración
                page = Page(width=Decimal(850), height=Decimal(764))
              #  page.set_page_size(PageSize.A4_LANDSCAPE) #Apaizar la pagina para que los registros no se
                doc.add_page(page)
                layout = SingleColumnLayout(page)
                #Reducir márgenes de la página para ganar espacio en la tabla
                layout.vertical_margin = Decimal(10)
                layout.horizontal_margin = Decimal(10)


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
                fin = min(inicio + max_personas_por_pagina, len(personas)) #Elige entre limite de pagina o el total de personas
                personas_pagina_actual = personas[inicio:fin]

                # Tabla
                tabla = Table(
                    number_of_rows=len(personas_pagina_actual) + 1,
                    number_of_columns=7,
                    column_widths=[
                        Decimal(30),  # ID
                        Decimal(120), # Nombre
                        Decimal(200), # Email
                        Decimal(90),  # DNI
                        Decimal(110),  # Teléfono
                        Decimal(100), # Fecha nacimiento
                        Decimal(55),  # Edad
                #        Decimal(85),  # Habilitada
                    ])

                # Encabezados
                headers = ["ID", "Nombre", "Email", "DNI", "Teléfono", "Fecha nacimiento", "Edad"]
                for h in headers:
                    tabla.add(Paragraph(h, font="Helvetica-Bold", horizontal_alignment=Alignment.CENTERED))
                    
                # Filas
                for p in personas_pagina_actual:
                    nombre = p.nombre if p.nombre else "Sin nombre"
                    email = p.email if p.email else "-"
                    dni = p.dni if p.dni else "-"
                    telefono = p.telefono if p.telefono else "-"
                    fecha_nacimiento = (
                        p.fecha_nacimiento.strftime("%d/%m/%Y")
                        if p.fecha_nacimiento 
                        else "-")
                    edad = str(calcular_edad(p.fecha_nacimiento)) if p.fecha_nacimiento else "-"
                   # habilitado = "Sí" if p.esta_habilitado else "No"

                    tabla.add(Paragraph(str(p.id), horizontal_alignment = Alignment.LEFT, respect_newlines_in_text=True))
                    tabla.add(Paragraph(nombre, horizontal_alignment = Alignment.LEFT, respect_newlines_in_text=True))
                    tabla.add(Paragraph(email, horizontal_alignment = Alignment.LEFT, respect_newlines_in_text=True))
                    tabla.add(Paragraph(dni, horizontal_alignment = Alignment.LEFT, respect_newlines_in_text=True))
                    tabla.add(Paragraph(telefono , horizontal_alignment = Alignment.LEFT, respect_newlines_in_text=True))
                    tabla.add(Paragraph(fecha_nacimiento , horizontal_alignment = Alignment.LEFT, respect_newlines_in_text=True))
                    tabla.add(Paragraph(edad , horizontal_alignment = Alignment.LEFT, respect_newlines_in_text=True))
                   # tabla.add(Paragraph(habilitado , horizontal_alignment = Alignment.LEFT, respect_newlines_in_text=True))

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
