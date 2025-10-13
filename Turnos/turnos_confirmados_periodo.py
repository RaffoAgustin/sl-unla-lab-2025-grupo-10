from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from DataBase.models import Turno
from DataBase.database import get_db

router = APIRouter()

@router.get("/reportes/turnos-confirmados")
def turnos_confirmados_periodo(
    desde: date = Query(..., description="Fecha en formato YYYY-MM-DD"), #Consulta obligatoria de la fecha inicial
    hasta: Optional[date] = Query(None, description="Fecha en formato YYYY-MM-DD"), #Consulta opcional de la fecha límite
    db: Session = Depends(get_db)  #Inyecta automáticamente una sesión de base de datos
):
    if (hasta != None) and (hasta < desde): #Si "hasta" fue indicado, verifica que sea mayor a "desde"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha 'hasta' no puede ser anterior a la fecha 'desde'"
        )

    try:
        #Consulta inicial
        turnosConfirmados = (
            db.query(Turno)
            .filter(
                Turno.estado == "Confirmado", #Aquellos turnos confirmados
                Turno.fecha >= desde) #Donde su fecha sea mas reciente que "desde"
                )
        
        if hasta: #Si "hasta" fue indicado...
            turnosConfirmados = turnosConfirmados.filter(Turno.fecha <= hasta) #...También filtro por las fechas más viejas que "hasta"

        #TODO: Meter la paginación
        #No se si hay que indicar en la query del endpoint al número de página, 
        #o simplemente devolver el json completo dividido entre 5 elementos.


        return turnosConfirmados
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error Inesperado"
        )