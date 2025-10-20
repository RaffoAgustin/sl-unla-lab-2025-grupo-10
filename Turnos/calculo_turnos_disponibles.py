from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas import FechaQuery
from DataBase.models import Turno
from DataBase.database import get_db
from Utils.config import HORARIOS_VALIDOS, ESTADOS_TURNO
from Utils.utils import validar_y_formatear_fecha

router = APIRouter()


@router.get("/turnos-disponibles")
def turnos_disponibles(fecha: str, db: Session = Depends(get_db)):
   
   fecha_formateada = validar_y_formatear_fecha(fecha)
   
   try:

        # Hago una consulta de los turnos donde la fecha sea la misma a la pedida por el usuario
        # Excluyo turnos cancelados o sin persona asignada (disponibles)
        turnos_ocupados = (db.query(Turno).filter(
            Turno.fecha == fecha_formateada,
            Turno.estado != ESTADOS_TURNO[1],  # No "Cancelado"
            Turno.persona_id.is_not(None)  # Solo turnos con persona asignada
        ).all())

        # Guardo las horas que ocupan esos turnos en un set, lo que evita repeticiones
        # Utilizo el método .strftime() para convertir t.hora en un string, ya que sino devolvería un objeto (datetime.time(14, 30))
        horas_ocupadas = {t.hora.strftime("%H:%M") for t in turnos_ocupados}

        horarios_disponibles = [
            h.strftime("%H:%M")  # devuelve string "09:00", "09:30", etc.
            for h in HORARIOS_VALIDOS
            if h.strftime("%H:%M") not in horas_ocupadas
        ]

        return {
            # Convierte nuevamente el objeto "fecha" a string
            "fecha": fecha_formateada.strftime("%Y-%m-%d"),
            # Devuelve la lista de horarios disponibles
            "horarios_disponibles": horarios_disponibles
        }
        
   except Exception as e:
       raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )
