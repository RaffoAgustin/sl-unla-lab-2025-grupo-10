from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas import FechaQuery
from DataBase.models import Turno
from DataBase.database import get_db
from variables import HORARIOS_VALIDOS

router = APIRouter()

@router.get("/turnos-disponibles")
def turnos_disponibles(query: FechaQuery = Depends(), db: Session = Depends(get_db)):
    try:

        #Hago una consulta de los turnos donde le fecha sea la misma a la pedida por el usuario
        turnos_ocupados = (db.query(Turno).filter(Turno.fecha == query.fecha, Turno.estado != "cancelado").all())

        #Guardo las horas que ocupan esos turnos en un set, lo que evita repeticiones
        #Utilizo el método .strftime() para convertir t.hora en un string, ya que sino devolvería un objeto (datetime.time(14, 30))
        horas_ocupadas = {t.hora.strftime("%H:%M") for t in turnos_ocupados}

        horarios_disponibles = [
            h.strftime("%H:%M")  # devuelve string "09:00", "09:30", etc.
            for h in HORARIOS_VALIDOS
            if h.strftime("%H:%M") not in horas_ocupadas
        ]
      
        return {
            "fecha": query.fecha.strftime("%Y-%m-%d"), #Convierte nuevamente el objeto "fecha" a string
            "horarios_disponibles": horarios_disponibles #Devuelve la lista de horarios disponibles
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )