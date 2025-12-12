from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from Utils.config import ESTADOS_TURNO, CANT_ELEMENTOS_X_PAGINA, CONFIG_PDF_TURNOS
from DataBase.models import Turno
from DataBase.database import get_db
from schemas import FechaQuery
from borb.pdf import Document, Page, SingleColumnLayout, Paragraph, PDF, FixedColumnWidthTable as Table
from fastapi.responses import StreamingResponse
from borb.pdf.canvas.color.color import HexColor
from borb.pdf.canvas.layout.layout_element import Alignment
from io import BytesIO
from decimal import Decimal

router = APIRouter()

@router.get("/pdf/turnos-confirmados-periodo")
def exportar_turnos_confirmados_periodo_pdf(
    desde: str = Query(..., description="Fecha futura en formato DD-MM-YYYY"), #Consulta obligatoria de la fecha inicial (Recibo un string)
    hasta: Optional[str] = Query(None, description="Fecha futura en formato DD-MM-YYYY"),  #Consulta opcional de la fecha límite
    pag: Optional[int] = Query(1, ge=1, description="Numero de pagina (minimo 1)"), #El predeterminado es 1 aunque no se ponga. ge=1 significa que debe ser mayor o igual a 1
    db: Session = Depends(get_db)  #Inyecta automáticamente una sesión de base de datos
):
    ## Ejemplo de Endpoint: 
    ## /reportes/pdf/turnos-confirmados-periodo?desde=20-10-2025&hasta=30-12-2025&pag=2

    try:
        # Convierto el string "desde" a un objeto date a través de la clase FechaQuery y sus validaciones
        fecha_desde = FechaQuery(fecha=desde).fecha 
                                #     ^ Recibe a "desde" como parámetro


        # Validar fecha hasta si existe
        fecha_hasta = None #Inicializo la variable

        if hasta:
            fecha_hasta = FechaQuery(fecha=hasta).fecha #Hago lo mismo que con "desde"
            if fecha_hasta < fecha_desde:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La fecha 'hasta' no puede ser anterior a la fecha 'desde'"
                )

        #Consulta inicial
        turnosConfirmados = (
            db.query(Turno)
            .filter(
                Turno.estado == ESTADOS_TURNO.Confirmado, #Aquellos turnos confirmados
                Turno.fecha >= fecha_desde) #Donde su fecha sea mas reciente que "desde"
                )
        
        if hasta: #Si "hasta" fue indicado...
            turnosConfirmados = turnosConfirmados.filter(Turno.fecha <= fecha_hasta) #...También filtro por las fechas más viejas que "hasta"
       
        #Si ningún registro cumple las condiciones, se lanza una excepción
        if not turnosConfirmados:
            raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No se encontraron registros"
                ) 
        
        paginaDeTurnos = (
            turnosConfirmados
            .order_by(Turno.fecha) #Ordeno por fecha de mas antiguo a más reciente
            .offset(CANT_ELEMENTOS_X_PAGINA * (pag-1)) #Offset es la cantidad de elementos salteados antes de mostrar.
            .limit(CANT_ELEMENTOS_X_PAGINA) #Limito la cantidad de registros por su variable
            .all() #Muestra todos los registros bajo estos parámetros
        )

        if not paginaDeTurnos:
            return {"mensaje":f"No hay registros en la página indicada (pag: {pag})"}
        
        #--- Acá termina la consulta ----

        cfg = CONFIG_PDF_TURNOS

        #Crear PDF
        doc = Document()

        # Cálculo inicial de cantidad de páginas
        max_turnos_por_pagina = cfg["max_rows"] - 2
        total_paginas = (len(paginaDeTurnos) + max_turnos_por_pagina - 1) // max_turnos_por_pagina #Division entera, no puede ser decimal
   
        #Bucle de páginas
        for num_pagina in range(total_paginas):   

            #Agrego una nueva pagina en cada bucle
            page = Page(width=cfg["page_width"], height=cfg["page_height"])
            doc.add_page(page)
            layout = SingleColumnLayout(page)

             # Título (Solo en primera pagina)
            if num_pagina == 0:
                layout.add(
                    Paragraph(
                        "Turnos confirmados en un periodo",
                        font="Helvetica-Bold",
                        font_size=20,
                        font_color=HexColor("#000000"),
                        horizontal_alignment = Alignment.CENTERED))
                
                subtitulo = (
                f"Desde {desde} hasta {hasta}"
                if hasta
                else f"Desde {desde} (sin límite)"
                )
                
                layout.add(Paragraph(subtitulo, font_size=Decimal(13)))
                layout.add(Paragraph(f"Página: {pag}", font_size=Decimal(13)))
        
                
        
            #Calibra la variable "Turnos_pagina_actual" para que tenga un valor de inicio y fin, cambiando en cada iteración del bucle
            inicio = num_pagina * max_turnos_por_pagina
            fin = min(inicio + max_turnos_por_pagina, len(paginaDeTurnos)) #Elige entre limite de pagina o el total de personas
            turnos_pagina_actual = paginaDeTurnos[inicio:fin]

            #Excluyo a Estado de la tabla, ya que es muy redundante
            idx_personaid = cfg["column_header_name"].index("Estado")
            column_widths_filtrados = [w for i, w in enumerate(cfg["column_widths"]) if i != idx_personaid]

            # Tabla
            tabla = Table(
                number_of_rows=len(turnos_pagina_actual) + 1, #Numero de filas
                number_of_columns=len(column_widths_filtrados), #Numero de columnas (Con Estado excluido)
                column_widths=column_widths_filtrados) #Ancho de columnas (Con Estado excluido)

            # Encabezados
            headers = cfg["column_header_name"] #Tomo los nombres de los encabezados del env
            # Para este endpoint, quitamos Estado
            headers_filtrados = [h for h in headers if h != "Estado"]
            
            for h in headers_filtrados:
                tabla.add(Paragraph(h, font="Helvetica-Bold", horizontal_alignment=Alignment.CENTERED))
    
            # Filas
            for t in turnos_pagina_actual:
                datos=[
                    str(t.id),
                    str(t.persona_id) if t.persona_id else "-",
                    t.fecha.strftime("%d/%m/%Y") if t.fecha else "-",
                    t.hora.strftime("%H:%M") if t.hora else "—",
                  #  t.estado if t.estado else "—"
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
            headers={"Content-Disposition": f"attachment; filename=turnos_confirmados_{desde}{"_"+ hasta if hasta else ""}.pdf"}
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error Inesperado"
        )