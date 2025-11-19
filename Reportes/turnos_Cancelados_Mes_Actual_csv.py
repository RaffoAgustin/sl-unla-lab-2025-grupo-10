from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import extract
from datetime import date
import pandas as pd
from fastapi.responses import FileResponse

from DataBase.database import get_db
from DataBase.models import Turno
from Utils.config import ESTADOS_TURNO, MESES

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

        df = pd.DataFrame(filas)

        archivo = f"turnos_cancelados_{hoy.year}_{hoy.month}.csv"

        with open(archivo, "w", encoding="utf-8", newline="") as f:
            f.write(f"Turnos cancelados - {MESES[hoy.month - 1]} {hoy.year}\n")
            df.to_csv(f, index=False)

        return FileResponse(
            archivo,
            media_type="text/csv",
            filename=archivo
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar CSV: {str(e)}")