from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from DataBase.models import Turno
from DataBase.database import get_db

router = APIRouter()

@router.patch("/turnos/{id}", status_code=status.HTTP_200_OK)
def eliminar_turno_logicamente(id: int, db: Session = Depends(get_db)):
    try:
        turno = db.get(Turno, id)
        if turno is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Turno con ID {id} no encontrado"
        )
        try:
            turno.estado = "cancelado"
            db.commit()
            return {"mensaje": f"Turno con ID {id} eliminado correctamente"}
        
        except Exception as e:
            db.rollback()
            raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar el turno"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )