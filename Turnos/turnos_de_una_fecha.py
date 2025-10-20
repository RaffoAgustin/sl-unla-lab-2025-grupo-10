from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from DataBase.models import Turno, Persona
from DataBase.database import get_db
import re
from datetime import datetime

from datetime import date

router = APIRouter()

# Obtener los turnos de una fecha
@router.get("/turnos-por-fecha")
def obtener_turnos_de_una_fecha(
    fecha: str,
    db: Session = Depends(get_db)  #Inyecta automáticamente una sesión de base de datos
):
    fecha = fecha.strip()

    # Validar caracteres permitidos
    if not re.fullmatch(r"[0-9/-]+", fecha):
        raise HTTPException(status_code=400, detail="La fecha solo puede contener números y '-' o '/'")

    # Convertir a date usando varios formatos
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            fecha_obj = datetime.strptime(fecha, fmt).date()
            break
        except ValueError:
            continue
    else:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Usar YYYY-MM-DD o DD/MM/YYYY")

    # Validar que no sea pasada
    if fecha_obj < date.today():
        raise HTTPException(status_code=400, detail="La fecha del turno no puede ser pasada")
    
    # Transformar fecha a formato "YYYY-MM-DD"
    fecha_iso = fecha_obj.isoformat()
    
    try:
        turnos = db.query(Turno).join(Persona).filter(Turno.fecha == fecha_obj).all()
        
        # Si no hay turnos en esa fecha
        if not turnos:
            return {"mensaje": f"No se encontraron turnos para la fecha {fecha_iso}"}
        
        return [
        {
            "Fecha": fecha_iso,
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
