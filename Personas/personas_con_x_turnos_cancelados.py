from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from DataBase.models import Turno, Persona
from DataBase.database import get_db

router = APIRouter()

@router.get("/reportes/turnos-cancelados")
def personas_con_turnos_cancelados(
    min: int = Query(..., description="Minimo de turnos cancelados"), #Pide al usuario el mínimo de Turnos cancelados (... significa obligatorio)
    db: Session = Depends(get_db)  #Inyecta automáticamente una sesión de base de datos
):
    if min < 0:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El valor minimo no puede ser negativo"
     )
    
    try:
        personas=(
            db.query(Persona) #Hace una consulta de personas
               .join(Turno) #Junto a sus turnos
               .filter(Turno.estado == "Cancelado") #Tomo unicamente a los turnos cancelados
               .group_by(Persona.id) #Agrupo a las personas según su id, necesario para que las func funcionen correctamente
               .having(func.count(Turno.id) >= min) #Filtro los grupos (cada persona) donde la cantidad de turnos (ya filtrados) sean mayores al minimo
               .all() #Muestro todas las personas con estas condiciones
        )

        return personas
    
    except Exception as e:
        print("Error en el reporte de turnos cancelados:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error Inesperado al obtener el reporte"
        )