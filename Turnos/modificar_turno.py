from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from DataBase.models import Turno, Persona
from DataBase.database import get_db
from schemas import TurnoUpdate
from Utils.config import ESTADOS_TURNO

router = APIRouter()

#Modificar un turno
@router.put("/turnos/{id}")
def modificar_turno(id: int, datos_turno: TurnoUpdate, db: Session=Depends(get_db)): #Usamos la plantilla TurnoCreate para los datos_turno
   #Guarda en variable "turno" un turno con el mismo id del db.
    try:
        turno = db.get(Turno, id)

        #Si no encuentra al turno, entonces lanza error 404
        if not turno:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Turno no encontrado"
            )

        existe = db.query(Turno).filter(
            Turno.fecha == datos_turno.fecha,
            Turno.hora == datos_turno.hora,
            Turno.estado != ESTADOS_TURNO[1] #Excluye a los turnos cancelados
        ).first()

        if existe:
            raise HTTPException(
                status_code=400,
                detail="Este turno ya está ocupado"
            )
        
        #Actualizo los datos del turno
        turno.fecha = datos_turno.fecha
        turno.hora = datos_turno.hora

        #Intento guardar los cambios
        try:
            db.commit()
            db.refresh(turno)
            return {
                "mensaje": f"Turno con ID {id} actualizado correctamente",
                "turno":{
                    "id": turno.id,
                    "fecha": turno.fecha,
                    "hora": turno.hora,
                    "estado": turno.estado
                }
            }
        
        #Si ocurre un error inesperado, lanza error 500
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error inesperado al actualizar turno"
            )
        
    except Exception as e:
        raise HTTPException(
        status_code=500,
        detail=f"Error interno del servidor: {str(e)}"
    )