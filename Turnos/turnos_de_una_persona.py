from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from DataBase.models import Turno, Persona
from DataBase.database import get_db
import re

router = APIRouter()

# Obtener los turnos de una fecha
@router.get("/turnos-por-persona")
def turnos_por_persona(dni: str = Query(..., description="DNI de 8 dígitos"), db: Session = Depends(get_db)):
    # Limpiar espacios
    dni = dni.strip()
    
    # Validar formato del DNI
    if not re.fullmatch(r"\d{8}", dni):
        raise HTTPException(status_code=400, detail="El DNI debe contener exactamente 8 números")
    
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