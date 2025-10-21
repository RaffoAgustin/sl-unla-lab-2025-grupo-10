from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from DataBase.models import Turno, Persona
from DataBase.database import get_db
from Utils.config import ESTADOS_TURNO

router = APIRouter()

# Confirmar un turno


@router.put("/turnos/{id}/confirmar")
def confirmar_turno(id: int, db: Session = Depends(get_db)):
    try:
        turno = db.get(Turno, id)
        if turno is None:
            raise HTTPException(
                status_code=404, detail=f"Turno con ID {id} no encontrado")

        # Validar que el turno tenga una persona asignada
        if turno.persona_id is None:
            raise HTTPException(
                status_code=400, detail=f"El turno con ID {id} no tiene una persona asignada")

        # Validar que el turno esté en estado "Pendiente"
        if turno.estado != ESTADOS_TURNO[0]:  # "Pendiente"
            raise HTTPException(
                status_code=400, detail=f"El turno con ID {id} no puede ser confirmado. Estado actual: {turno.estado}")

        turno.estado = ESTADOS_TURNO[2]  # "Confirmado"
        db.commit()
        db.refresh(turno)

        return {
            "Turno confirmado exitosamente": {
                "id": turno.id,
                "fecha": turno.fecha,
                "hora": turno.hora,
                "estado": turno.estado,
                "persona_id": turno.persona_id
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al confirmar el turno con ID {id}: {str(e)}")
