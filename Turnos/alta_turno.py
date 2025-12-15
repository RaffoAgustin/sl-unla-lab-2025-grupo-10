from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from DataBase.database import get_db
from DataBase.models import Turno, Persona
from schemas import TurnoCreate
from Utils.utils import supera_max_cancelaciones
from Utils.config import HORARIOS_VALIDOS
from Utils.config import ESTADOS_TURNO, MAX_CANCELADOS, MAX_MESES_CANCELADOS

router = APIRouter()

# Crear un nuevo Turno
@router.post("/turno", status_code=status.HTTP_201_CREATED)
def crear_turno(datos_turno: TurnoCreate, db: Session = Depends(get_db)):
    try:
        existe = db.query(Turno).filter(
            Turno.fecha == datos_turno.fecha,
            Turno.hora == datos_turno.hora,
            Turno.estado != ESTADOS_TURNO.Cancelado #Excluye a los turnos cancelados
        ).first()

        if existe:
            raise HTTPException(
                status_code=400,
                detail="Este turno ya está ocupado"
            )
        
        persona = db.query(Persona).filter(Persona.id == datos_turno.persona_id).first()
        if not persona:
            raise HTTPException(status_code=400, detail="La persona indicada no existe")
        
        if not persona.esta_habilitado:
            motivo = "La persona no está habilitada para sacar turnos"
            if supera_max_cancelaciones(db, persona.id):
                motivo += f" por exceso de cancelaciones en los últimos {MAX_MESES_CANCELADOS} meses"

            raise HTTPException(status_code=400, detail=motivo)

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