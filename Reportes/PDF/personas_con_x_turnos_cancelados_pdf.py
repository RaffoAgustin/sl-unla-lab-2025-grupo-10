from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from Utils.config import ESTADOS_TURNO
from DataBase.models import Turno, Persona
from DataBase.database import get_db
from borb.pdf import Document, Page, SingleColumnLayout, Paragraph, PDF
from pathlib import Path
from fastapi.responses import FileResponse
from Utils.utils import calcular_edad

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

        # Crear carpeta si no existe
        pdf_path = Path(f"Reportes/PDF_Generados/turnos_cancelados_min_{min}.pdf")
        pdf_path.parent.mkdir(parents=True, exist_ok=True)

        # Crear PDF
        doc = Document()
        page = Page()
        doc.append_page(page)
        layout = SingleColumnLayout(page)

        # Título
        layout.append_layout_element(Paragraph(f"Personas con {min} turno/s cancelados o más"))
        
        personas=(
                db.query(Persona) #Hace una consulta de personas
                .join(Turno) #Junto a sus turnos
                .filter(Turno.estado == ESTADOS_TURNO[1]) #Tomo unicamente a los turnos cancelados
                .group_by(Persona.id) #Agrupo a las personas según su id, necesario para que las func funcionen correctamente
                .having(func.count(Turno.id) >= min) #Filtro los grupos (cada persona) donde la cantidad de turnos (ya filtrados) sean mayores al minimo
                .all() #Muestro todas las personas con estas condiciones
            )

        if not personas:
            return {"mensaje": f"No se encontraron personas con mas de {min} turnos cancelados"}
        
        
        #Por cada registro de personas que cumplan las condiciones, agrego un parrafo.
        for p in personas:
            texto = (
                f"ID: {p.id}, Nombre: {p.nombre}, Email: {p.email}, "
                f"DNI: {p.dni}, Teléfono: {p.telefono}, Fecha nacimiento: {p.fecha_nacimiento}, "
                f"Edad: {calcular_edad(p.fecha_nacimiento)}, Habilitada: {p.esta_habilitado}"
            )
            layout.append_layout_element(Paragraph(texto))

        # Guardar PDF
        PDF.write(what=doc, where_to=str(pdf_path))

        # Devolver PDF
        return FileResponse(
            path=str(pdf_path),
            media_type="application/pdf",
            filename=pdf_path.name
        )
    
    except Exception as e:
        print("Error en el reporte de turnos cancelados:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error Inesperado al obtener el reporte"
        )