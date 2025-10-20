from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from DataBase.models import Turno, Persona
from DataBase.database import get_db
from Utils.config import ESTADOS_TURNO

router = APIRouter()

# Cancelar un turno


@router.put("/turnos/{id}/cancelar")
def cancelar_turno(id: int, db: Session = Depends(get_db)):
    try:
        turno = db.get(Turno, id)
        if turno is None:
            raise HTTPException(
                status_code=404, detail=f"Turno con ID {id} no encontrado")

        if turno.estado == ESTADOS_TURNO[3]:
            raise HTTPException(
                status_code=400, detail=f"El turno con ID {id} ya fue asistido y no puede ser cancelado")

        if turno.estado == ESTADOS_TURNO[1]:
            raise HTTPException(
                status_code=400, detail=f"El turno con ID {id} ya fue cancelado previamente")

        # La cancelacion libera el turno para que otra persona lo pueda tomar
        turno.estado = ESTADOS_TURNO[1]  # "Cancelado"
        db.commit()
        db.refresh(turno)

        return {
            "Turno cancelado exitosamente": {
                "id": turno.id,
                "fecha": turno.fecha,
                "hora": turno.hora,
                "estado": turno.estado,
                "persona_id": turno.persona_id 
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al cancelar el turno con ID {id}: {str(e)}")
