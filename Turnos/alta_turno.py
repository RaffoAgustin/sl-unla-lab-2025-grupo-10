from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from DataBase.database import get_db
from DataBase.models import Turno, Persona
from schemas import TurnoCreate
from Utils.utils import validar_cancelaciones
from Utils.config import HORARIOS_VALIDOS

router = APIRouter()

# Crear un nuevo Turno
@router.post("/turno", status_code=status.HTTP_201_CREATED)
def crear_turno(datos_turno: TurnoCreate, db: Session = Depends(get_db)):
    try:
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
        
        validar_cancelaciones(db, datos_turno.persona_id)

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
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )