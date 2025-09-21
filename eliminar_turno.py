from fastapi import APIRouter, HTTPException, status, Depends
from models import Turno
from sqlalchemy.orm import Session
from database import get_db

router = APIRouter()

@router.delete("/turnos/{id}", status_code=status.HTTP_200_OK)
def eliminar_turno(id: int, db: Session = Depends(get_db)):
        turno = db.get(Turno, id)
        if turno is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Turno con ID {id} no encontrado"
        )
        try:
            db.delete(turno)
            db.commit()
            return {"mensaje": f"Turno con ID {id} eliminado correctamente"}
        
        except Exception as e:
            db.rollback()
            raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el turno"
        )