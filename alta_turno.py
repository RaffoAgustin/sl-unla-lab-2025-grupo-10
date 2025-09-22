from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Turno, Persona
from schemas import TurnoCreate
from datetime import datetime, date, time, timedelta

router = APIRouter()

# Crear un nuevo Turno
@router.post("/turno", status_code=status.HTTP_201_CREATED)
def crear_turno(datos_turno: TurnoCreate, db: Session = Depends(get_db)):

    if isinstance(datos_turno.hora, str):
        try:
            datos_turno.hora = datetime.strptime(datos_turno.hora, "%H:%M").time()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Formato de hora inválido, debe ser HH:MM"
            )

    horarios_validos = [
        time(9,0), time(9,30), time(10,0), time(10,30), time(11,0), time(11,30),
        time(12,0), time(12,30), time(13,0), time(13,30), time(14,0), time(14,30),
        time(15,0), time(15,30), time(16,0), time(16,30), time(17,0)
    ]

    if datos_turno.hora not in horarios_validos:
        raise HTTPException(
            status_code=400,
            detail="El turno debe estar entre las 09:00 y 17:00 en intervalos de 30 minutos"
        )
    
    existe = db.query(Turno).filter(
        Turno.fecha == datos_turno.fecha,
        Turno.hora == datos_turno.hora
    ).first()

    if existe:
        raise HTTPException(
            status_code=400,
            detail="Este turno ya está ocupado"
        )
    
    persona = db.query(Persona).filter(Persona.id == datos_turno.persona_id).first()
    if not persona:
        raise HTTPException(status_code=400, detail="La persona indicada no existe")
    

    hace_6_meses = date.today() - timedelta(days=180)

    cancelados = db.query(Turno).filter(
        Turno.persona_id == datos_turno.persona_id,
        Turno.estado == "cancelado", 
        Turno.fecha >= hace_6_meses
    ).count()

    if cancelados >= 5:
        raise HTTPException(
            status_code=400,
            detail="No se puede asignar el turno: la persona tiene 5 o más turnos cancelados en los últimos 6 meses"
        )

    turno_nuevo = Turno(
        fecha=datos_turno.fecha,
        hora=datos_turno.hora,
        estado="Pendiente", 
        persona_id=persona.id
    )

    db.add(turno_nuevo)
    try:
        db.commit()
        db.refresh(turno_nuevo)

        return {
            "mensaje": "Turno creado correctamente",
            "turno": {
                "id": turno_nuevo.id,
                "fecha": turno_nuevo.fecha,
                "hora": str(turno_nuevo.hora),
                "estado": turno_nuevo.estado,
                "persona_id": turno_nuevo.persona_id
            }
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Error al crear un nuevo Turno: {e}"
        )