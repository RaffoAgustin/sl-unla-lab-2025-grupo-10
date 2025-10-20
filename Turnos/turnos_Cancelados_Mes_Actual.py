from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import extract, func
from DataBase.database import get_db
from DataBase.models import Turno
from Utils.config import ESTADOS_TURNO, MESES

router = APIRouter()


@router.get("/turnos-cancelados-por-mes")
def turnos_cancelados_mes_actual(db: Session = Depends(get_db)):
    hoy = date.today()

    grupos = db.query(
        Turno.fecha,
        func.count(Turno.id).label("cantidad")
    ).filter(
        Turno.estado == ESTADOS_TURNO[1],
        extract('year', Turno.fecha) == hoy.year,
        extract('month', Turno.fecha) == hoy.month
    ).group_by(Turno.fecha).all()

    fechas = []
    total_cancelados = 0

    for fecha, cantidad in grupos:
        turnos_fecha = db.query(Turno).filter(
            Turno.estado == ESTADOS_TURNO[1],
            Turno.fecha == fecha
        ).all()

        fechas.append({
            "fecha": str(fecha),
            "cantidad": cantidad,
            "turnos": [
                {
                    "id": t.id,
                    "persona_id": t.persona_id,
                    "hora": str(t.hora),
                    "estado": t.estado
                }
                for t in turnos_fecha
            ]
        })

        total_cancelados += cantidad

    return {
        "anio": hoy.year,
        "mes": MESES[hoy.month-1],
        "cantidad": total_cancelados,
        "fechas": fechas
    }
