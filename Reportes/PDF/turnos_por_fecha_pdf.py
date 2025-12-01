from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from DataBase.models import Turno, Persona
from DataBase.database import get_db
from Utils.utils import validar_y_formatear_fecha_especial
import pandas as pd
from fastapi.responses import FileResponse
from pathlib import Path
from borb.pdf import Document, Page, SingleColumnLayout, Paragraph, PDF

router = APIRouter()

# Obtener los turnos de una fecha
@router.get("/pdf/turnos-por-fecha")
def exportar_turnos_de_una_fecha_csv(fecha: str, db: Session = Depends(get_db)):
    try:
        fecha_formateada = validar_y_formatear_fecha_especial(fecha)
        turnos = db.query(Turno).join(Persona).filter(Turno.fecha == fecha_formateada).all()
        
        # Si no hay turnos en esa fecha
        if not turnos:
            return {"mensaje": f"No se encontraron turnos para la fecha {fecha_formateada}"}
        
        # Diccionario auxiliar para agrupar por persona
        personas_dict = {}
        
        for t in turnos:
            dni = t.persona.dni
            
            # Si la persona no está aún en el diccionario, la agregamos
            if dni not in personas_dict:
                personas_dict[dni] = {
                "Nombre": t.persona.nombre,
                "DNI": dni,
                "Turnos": [] 
                }
                
            # Agregamos el turno a la lista de esa persona
            personas_dict[dni]["Turnos"].append(
                {"ID":t.id,
                 "Hora": t.hora.strftime("%H:%M"),
                 "Estado": t.estado })
                
        # Crear carpeta si no existe
        pdf_path = Path(f"Reportes/PDF_Generados/turnos_por_fecha{fecha_formateada}.pdf")
        pdf_path.parent.mkdir(parents=True, exist_ok=True)

        # Crear PDF
        doc = Document()
        page = Page()
        doc.append_page(page)
        layout = SingleColumnLayout(page)

        # Título
        layout.append_layout_element(Paragraph(f"Turnos en la fecha {fecha_formateada}"))
            
        # Agregar cada turno como párrafo
        for persona in personas_dict.values():
            for turno in persona["Turnos"]:
                texto = (
                    f"Nombre: {persona['Nombre']}, "
                    f"DNI: {persona['DNI']}, "
                    f"ID Turno: {turno['ID']}, "
                    f"Hora: {turno['Hora']}, "
                    f"Estado: {turno['Estado']}")
            
                layout.append_layout_element(Paragraph(texto))

        # Guardar PDF
        PDF.write(what=doc, where_to=str(pdf_path))

        # Devolver PDF
        return FileResponse(
            path=str(pdf_path),
            media_type="application/pdf",
            filename=pdf_path.name
            )
    
    except Exception as e: raise HTTPException(status_code=500, detail=f"Error al obtener los turnos de la fecha {fecha}: {str(e)}")