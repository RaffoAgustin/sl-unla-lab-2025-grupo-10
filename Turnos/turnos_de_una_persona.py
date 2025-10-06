from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from DataBase.models import Turno, Persona
from DataBase.database import get_db

from datetime import date

router = APIRouter()

# Obtener los turnos de una fecha
@router.get("/reportes/turnos-por-persona")
def obtener_turnos_de_una_persona(dni: str, db: Session = Depends(get_db)):
    try:
        turnos = db.query(Turno).join(Persona).filter(
            Turno.persona_id == Persona.id,
            Persona.dni == dni
            ).all()
        
        # Si esa persona no tiene turnos:
        if not turnos:
            return {"mensaje": f"No se encontraron turnos para la persona con DNI = {dni}"}
    
        return [
        {
            "ID": t.id,
            "Fecha": t.fecha,
            "Hora": t.hora,
            "Estado": t.estado,
        } 
        for t in turnos
    ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los turnos de la persona con DNI = {dni}: {str(e)}")