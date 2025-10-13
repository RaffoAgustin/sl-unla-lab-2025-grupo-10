from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from DataBase.models import Persona
from DataBase.database import get_db

router = APIRouter()

# Listado de las personas en la BD


@router.get("/personas")
def listado_personas(db: Session = Depends(get_db)):
    try:
        personas = db.query(Persona).all()
        if not personas:
            raise HTTPException(
                status_code=404, detail="No se encontraron personas")

        return [vars(persona) for persona in personas]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )
