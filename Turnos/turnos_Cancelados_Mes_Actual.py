from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import extract, func
from fastapi import HTTPException
from DataBase.database import get_db
from DataBase.models import Turno
from Utils.config import ESTADOS_TURNO, MESES

router = APIRouter()



@router.get("/turnos-cancelados-por-mes")
def turnos_cancelados_mes_actual(db: Session = Depends(get_db)):
    try:
        hoy = date.today()

        print("Valor usado para filtrar:", repr(ESTADOS_TURNO.Cancelado.value))

        turnos = db.query(Turno).filter(
            Turno.estado == ESTADOS_TURNO.Cancelado,
            extract('year', Turno.fecha) == hoy.year,
            extract('month', Turno.fecha) == hoy.month
        ).all()

        fechas_dict = {}

        for t in turnos:
            fecha_str = str(t.fecha)

            if fecha_str not in fechas_dict:
                fechas_dict[fecha_str] = {
                    "fecha": fecha_str,
                    "cantidad": 0,
                    "turnos": []
                }

            fechas_dict[fecha_str]["cantidad"] += 1
            fechas_dict[fecha_str]["turnos"].append({
                "id": t.id,
                "persona_id": t.persona_id,
                "hora": str(t.hora),
                "estado": t.estado
            })

        total_cancelados = len(turnos)

        return {
            "anio": hoy.year,
            "mes": MESES[hoy.month - 1],
            "cantidad": total_cancelados,
            "fechas": list(fechas_dict.values())
        }

    except Exception as e:
        print("Error en /turnos-cancelados-por-mes:", str(e))
        raise HTTPException(status_code=500, detail="Error interno del servidor")