from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from DataBase.models import Turno, Persona
from DataBase.database import get_db
from Utils.utils import validar_dni
import pandas as pd
from fastapi.responses import FileResponse

router = APIRouter()

# Obtener los turnos de una persona
@router.get("/csv/turnos-por-persona")
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

        # Si esa persona no tiene turnos:
        if not turnos:
            return {"mensaje": f"No se encontraron turnos para la persona con DNI = {dni}"}

        turnos_persona = {
            f"Turnos de {turnos[0].persona.nombre if turnos else None}": [
                {
                    "ID": t.id,
                    "Fecha": t.fecha.strftime("%Y/%m/%d"),
                    "Hora": t.hora.strftime("%H:%M"),
                    "Estado": t.estado,
                } for t in turnos
            ]
        }

        # Convertir a DataFrame y guardar CSV
        nombre_archivo = f"Reportes/turnos_{dni}.csv"
        df = pd.DataFrame(turnos_persona)
        df.to_csv(nombre_archivo, index=False, encoding="utf-8-sig")

        # Retornar el archivo como descarga
        return FileResponse(
            nombre_archivo,
            media_type="text/csv",
            filename=f"turnos_{dni}.csv"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los turnos de la persona con DNI = {dni}: {str(e)}"
        )
