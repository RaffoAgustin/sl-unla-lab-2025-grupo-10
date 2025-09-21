#Codigo para mostrar una sola persona de la base de datos

from fastapi import APIRouter, HTTPException, Depends
from models import Persona
from database import get_db
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/personas/{id}")
def obtener_persona(id: int, db: Session = Depends(get_db)):
    persona = db.get(Persona, id)
    if persona is None:
        raise HTTPException(status_code=404, detail="La persona no fue encontrada en la base de datos")
    return vars(persona)
