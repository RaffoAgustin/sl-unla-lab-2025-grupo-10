from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from DataBase.models import Turno, Persona
from DataBase.database import get_db
from Utils.utils import validar_dni
import pandas as pd
from io import StringIO
from fastapi.responses import StreamingResponse

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
        nombre_persona = turnos[0].persona.nombre

        filas = []
        
        for t in turnos:
            filas.append({
                "ID Turno": t.id,
                "Fecha": t.fecha.strftime("%Y/%m/%d"),
                "Hora": t.hora.strftime("%H:%M"),
                "Estado": t.estado
            })

        # Crear DataFrame con formato tabular limpio
        df = pd.DataFrame(filas)
        
        buffer = StringIO()
        buffer.write(f"Nombre: {nombre_persona}\n")
        df.to_csv(buffer, index=False, sep=";", encoding="utf-8-sig")
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=turnos_{nombre_persona}.csv"}
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los turnos de la persona con DNI = {dni}: {str(e)}"
        )
