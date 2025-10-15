from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from DataBase.models import Persona
from DataBase.database import get_db

router = APIRouter()

# Eliminar una persona
@router.delete("/personas/{id}", status_code=status.HTTP_200_OK)
def eliminar_persona(id: int, db: Session = Depends(get_db)):
    try:
        persona = db.get(Persona, id)
        if persona is None:
            raise HTTPException(status_code=404, detail=f"Persona con ID {id} no encontrada")
        try:
            db.delete(persona)
            db.commit()
            return {"mensaje": f"La persona con ID {id} se eliminó correctamente"}
        
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error al eliminar la persona con ID {id}")
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )