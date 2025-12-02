from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import extract
from datetime import date
from DataBase.database import get_db
from DataBase.models import Turno
from Utils.config import ESTADOS_TURNO, MESES

import pandas as pd
from io import StringIO
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.get("/csv/turnos-cancelados-por-mes")
def exportar_turnos_cancelados_mes_actual_csv(db: Session = Depends(get_db)):
    try:
        hoy = date.today()

        # Obtener turnos cancelados del mes actual
        turnos = db.query(Turno).filter(
            Turno.estado == ESTADOS_TURNO[1],
            extract('year', Turno.fecha) == hoy.year,
            extract('month', Turno.fecha) == hoy.month
        ).all()

        if not turnos:
            return {"mensaje": f"No hay turnos cancelados en {MESES[hoy.month - 1]} {hoy.year}"}

        filas = []
        for t in turnos:
            filas.append({
                "ID": t.id,
                "Persona ID": t.persona_id,
                "Fecha": str(t.fecha),
                "Hora": str(t.hora),
                "Estado": t.estado
            })
        
        # Crear DataFrame con formato tabular limpio
        df = pd.DataFrame(filas)
        
        buffer = StringIO()
        df.to_csv(buffer, index=False, sep=";", encoding="utf-8-sig")
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=turnos_cancelados_{hoy.year}_{hoy.month}.csv"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar CSV: {str(e)}")