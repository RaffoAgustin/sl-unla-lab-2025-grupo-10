from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from DataBase.models import Turno, Persona
from DataBase.database import get_db
from Utils.utils import validar_dni

router = APIRouter()

# Obtener los turnos de una fecha
@router.get("/turnos-por-persona")
def turnos_por_persona(dni: str = Query(..., description="DNI de 8 dígitos"), db: Session = Depends(get_db)):
    
    validar_dni(dni)
    
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