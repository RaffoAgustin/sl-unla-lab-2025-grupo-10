from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from DataBase.models import Persona, Turno
from DataBase.database import get_db
from variables import ESTADO_TURNO

router = APIRouter()


@router.get("/turnos/{id}/confirmar")
def confirmar_turno(id: int, db: Session = Depends(get_db)):
    try:
        # LOGICA
        return

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )
