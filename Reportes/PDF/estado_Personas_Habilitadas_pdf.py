from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from pathlib import Path

from borb.pdf import Document, Page, SingleColumnLayout, Paragraph, PDF

from DataBase.database import get_db
from DataBase.models import Persona
from Utils.utils import calcular_edad

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

        if not personas:
            return {"mensaje": f"No se encontraron personas con habilitada={habilitada}"}

        # Crear carpeta si no existe
        pdf_path = Path(f"Reportes/PDF_Generados/estado_personas_{habilitada}.pdf")
        pdf_path.parent.mkdir(parents=True, exist_ok=True)

        # Crear PDF
        doc = Document()
        page = Page()
        doc.append_page(page)
        layout = SingleColumnLayout(page)

        # Título
        layout.append_layout_element(Paragraph(f"Personas con habilitada={habilitada}"))

        # Agregar cada persona como párrafo
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
        print("Error en /pdf/estado-personas:", str(e))
        raise HTTPException(status_code=500, detail="Error interno del servidor")
