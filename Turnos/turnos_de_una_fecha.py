from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from DataBase.models import Turno, Persona
from DataBase.database import get_db

from datetime import date

router = APIRouter()

# Obtener los turnos de una fecha
@router.get("/reportes/turnos-por-fecha")
def obtener_turnos_de_una_fecha(
    fecha: date = Query(..., description="Fecha en formato YYYY-MM-DD"), #Pide al usuario un elemento date (... significa obligatorio)
    db: Session = Depends(get_db)  #Inyecta automáticamente una sesión de base de datos
):
    try:
        turnos = db.query(Turno).join(Persona).filter(Turno.fecha == fecha).all()
        
        # Si no hay turnos en esa fecha
        if not turnos:
            return {"mensaje": f"No se encontraron turnos para la fecha {fecha}"}
        
        return [
        {
            "Fecha": t.fecha,
            "Hora": t.hora,
            "Estado": t.estado,
            "Persona": {
                "nombre": t.persona.nombre,
                "dni": t.persona.dni,
            } if t.persona else None     
        } for t in turnos
    ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los turnos de la fecha {fecha}: {str(e)}")
