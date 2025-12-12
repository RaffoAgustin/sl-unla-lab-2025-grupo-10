from fastapi import HTTPException
from sqlalchemy.orm import Session
from dateutil.relativedelta import relativedelta
from datetime import datetime, date, timedelta
from Utils.config import MAX_CANCELADOS, ESTADOS_TURNO
import re

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
        Turno.estado == ESTADOS_TURNO.Confirmado,  # "Confirmado"
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
            turno.estado = ESTADOS_TURNO.Asistido  # "Asistido"

        db.commit()
        return len(turnos_vencidos)

    return 0

def validar_y_formatear_fecha(fecha: str):
    fecha = fecha.strip()

    # Validar caracteres permitidos
    if not re.fullmatch(r"[0-9/-]+", fecha):
        raise HTTPException(status_code=400, detail="La fecha solo puede contener números y '-' o '/'")

    # Convertir a date usando varios formatos
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            fecha_obj = datetime.strptime(fecha, fmt).date()
            break
        except ValueError:
            continue
    else:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Usar YYYY-MM-DD o DD/MM/YYYY")

    # Validar que no sea pasada
    if fecha_obj < date.today():
        raise HTTPException(status_code=400, detail="La fecha del turno no puede ser pasada")
    
    # Devuelvo objeto date
    return fecha_obj

def validar_y_formatear_fecha_especial(fecha: str):
    fecha = fecha.strip()

    # Validar caracteres permitidos
    if not re.fullmatch(r"[0-9/-]+", fecha):
        raise HTTPException(status_code=400, detail="La fecha solo puede contener números y '-' o '/'")

    # Convertir a date usando varios formatos
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            fecha_obj = datetime.strptime(fecha, fmt).date()
            break
        except ValueError:
            continue
    else:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Usar YYYY-MM-DD o DD/MM/YYYY")
    
    # Devuelvo objeto date
    return fecha_obj

def validar_dni(dni: str):
    # Limpiar espacios
    dni = dni.strip()
    
    # Validar formato del DNI
    if not re.fullmatch(r"\d{8}", dni):
        raise HTTPException(status_code=400, detail="El DNI debe contener exactamente 8 números")

def validar_y_convertir_fecha(v: str) -> date:
        v = v.strip()

        # Validar caracteres permitidos (solo números y separadores '-' o '/')
        if not re.fullmatch(r"[0-9/-]+", v):
            raise ValueError("La fecha solo puede contener números y los separadores '-' o '/'")

        # Intentar convertir a date usando varios formatos
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                fecha_obj = datetime.strptime(v, fmt).date()
                break
            except ValueError:
                continue
        else:
            raise ValueError("Formato de fecha inválido. Usar YYYY-MM-DD o DD/MM/YYYY")

        # Validar que no sea fecha pasada
        if fecha_obj < date.today():
            raise ValueError("La fecha del turno no puede ser pasada")

        return fecha_obj  # Devuelve un date listo para usar en SQLAlchemy