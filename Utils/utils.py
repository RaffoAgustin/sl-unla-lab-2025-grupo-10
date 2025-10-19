from fastapi import HTTPException
from sqlalchemy.orm import Session
from dateutil.relativedelta import relativedelta
from datetime import datetime, date, timedelta
from Utils.config import MAX_CANCELADOS, ESTADOS_TURNO


def calcular_edad(fecha):
    if isinstance(fecha, date):
        return relativedelta(date.today(), fecha).years
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


def actualizar_turnos_vencidos(db: Session):
    # Actualiza automáticamente los turnos confirmados que ya pasaron de fecha
    # y los marca como 'Asistido'

    # Import local para evitar circular import
    from DataBase.models import Turno

    hoy = date.today()
    ahora = datetime.now().time()

    # Buscar turnos confirmados que ya pasaron
    turnos_vencidos = db.query(Turno).filter(
        Turno.estado == ESTADOS_TURNO[2],  # "Confirmado"
        (
            (Turno.fecha < hoy) |  # Fechas pasadas
            (
                (Turno.fecha == hoy) &
                (Turno.hora < ahora)  # Hoy pero hora pasada
            )
        )
    ).all()

    # Actualizar a "Asistido"
    if turnos_vencidos:
        for turno in turnos_vencidos:
            turno.estado = ESTADOS_TURNO[3]  # "Asistido"

        db.commit()
        return len(turnos_vencidos)

    return 0
