from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Turno
from schemas import TurnoCreate

router = APIRouter()

# Crear una nuevo Turno
@router.post("/turno", status_code=status.HTTP_201_CREATED)
def crear_turno(datos_turno: TurnoCreate, db: Session = Depends(get_db)):
    turno_nuevo = Turno(
        fecha=datos_turno.fecha,
        hora=datos_turno.hora,
        estado="Pendiente", 
        persona_id=datos_turno.persona_id  
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