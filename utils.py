from fastapi import HTTPException
from sqlalchemy.orm import Session
from dateutil.relativedelta import relativedelta
from datetime import datetime, date, timedelta
from variables import MAX_CANCELADOS

def calcular_edad(fecha):
    for f in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try: 
            fecha = datetime.strptime(fecha, f).date()
            break
        except:
            pass
    else:
        raise ValueError("Formato no válido.")
    return relativedelta(date.today(), fecha).years

def validar_cancelaciones(db: Session, persona_id: int, meses: int = 6):
    # Import local para romper la circularidad
    from DataBase.models import Turno

    if db.query(Turno).filter(
        Turno.persona_id == persona_id,
        Turno.estado == "cancelado",
        Turno.fecha >= date.today() - timedelta(days=30*meses)
    ).count() >= MAX_CANCELADOS:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede asignar el turno: la persona tiene {MAX_CANCELADOS} o más turnos cancelados en los últimos {meses} meses"
        )
