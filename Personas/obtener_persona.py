#Codigo para mostrar una sola persona de la base de datos

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from DataBase.models import Persona
from DataBase.database import get_db

router = APIRouter()

@router.get("/personas/{id}")
def obtener_persona(id: int, db: Session = Depends(get_db)):
    persona = db.get(Persona, id)
    if persona is None:
        raise HTTPException(status_code=404, detail="La persona no fue encontrada en la base de datos")
    return vars(persona)
