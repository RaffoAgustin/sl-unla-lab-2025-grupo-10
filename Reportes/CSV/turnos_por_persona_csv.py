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

        # Crear lista tabular de turnos
        filas = []
        for t in turnos:
            filas.append({
                "ID Turno": t.id,
                "Fecha": t.fecha.strftime("%Y/%m/%d"),
                "Hora": t.hora.strftime("%H:%M"),
                "Estado": t.estado
            })

        # Crear DataFrame
        df = pd.DataFrame(filas)

        # Guardar CSV con título
        nombre_archivo = f"Reportes/turnos_{dni}.csv"
        with open(nombre_archivo, "w", encoding="utf-8", newline='') as f:
            f.write(f"Turnos de {turnos[0].persona.nombre}: DNI {turnos[0].persona.dni}\n")
            df.to_csv(f, index=False)

        # Retornar archivo como descarga
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
