from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from DataBase.models import Turno, Persona
from DataBase.database import get_db
from Utils.utils import validar_y_formatear_fecha

router = APIRouter()
    
# Obtener los turnos de una fecha
@router.get("/turnos-por-fecha")
def obtener_turnos_de_una_fecha(
    fecha: str,
    db: Session = Depends(get_db)  #Inyecta automáticamente una sesión de base de datos
):
    fecha_formateada = validar_y_formatear_fecha(fecha)
    
    try:
        turnos = db.query(Turno).join(Persona).filter(Turno.fecha == fecha_formateada).all()
        
        # Si no hay turnos en esa fecha
        if not turnos:
            return {"mensaje": f"No se encontraron turnos para la fecha {fecha_formateada}"}
        
        return [
        {
            "Fecha": fecha_formateada,
            "Hora": t.hora,
            "Estado": t.estado,
            "Persona": {
                "nombre": t.persona.nombre,
                "dni": t.persona.dni,
            } if t.persona else None     
        } for t in turnos
    ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los turnos de la fecha {fecha_formateada}: {str(e)}")
