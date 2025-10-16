from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from Utils.config import ESTADO_TURNO
from DataBase.models import Turno
from DataBase.database import get_db

router = APIRouter()

@router.get("/reportes/turnos-confirmados")
def turnos_confirmados_periodo(
    desde: date = Query(..., description="Fecha en formato YYYY-MM-DD"), #Consulta obligatoria de la fecha inicial
    hasta: Optional[date] = Query(None, description="Fecha en formato YYYY-MM-DD"), #Consulta opcional de la fecha límite
    pag: Optional[int] = Query(1, ge=1, description="Numero de pagina (minimo 1)"), #El predeterminado es 1 aunque no se ponga. ge=1 significa que debe ser mayor o igual a 1
    db: Session = Depends(get_db)  #Inyecta automáticamente una sesión de base de datos
):
    ## Ejemplo de Endpoint: 
    ## /reportes/turnos-confirmados?desde=2024-02-17&hasta=2025-12-24&pag=3
    try:
        
        if hasta and (hasta < desde): #Si "hasta" fue indicado, verifica que sea mayor a "desde"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha 'hasta' no puede ser anterior a la fecha 'desde'"
            )

        #Consulta inicial
        turnosConfirmados = (
            db.query(Turno)
            .filter(
                Turno.estado == ESTADO_TURNO[2], #Aquellos turnos confirmados
                Turno.fecha >= desde) #Donde su fecha sea mas reciente que "desde"
                )
        
        if hasta: #Si "hasta" fue indicado...
            turnosConfirmados = turnosConfirmados.filter(Turno.fecha <= hasta) #...También filtro por las fechas más viejas que "hasta"

        #TODO: La variable "cantElementosXPagina" debería ser una variable de entorno, quizas.
        cantElementosXPagina = 5

        paginaDeTurnos = (
            turnosConfirmados
            .order_by(Turno.fecha) #Ordeno por fecha de mas antiguo a más reciente
            .offset(cantElementosXPagina * (pag-1)) #Offset es la cantidad de elementos salteados antes de mostrar.
            .limit(cantElementosXPagina) #Limito la cantidad de registros por su variable
            .all() #Muestra todos los registros bajo estos parámetros
        )

        return {
            "pagina": pag,
            "cantElementos": cantElementosXPagina,
            "turnos": paginaDeTurnos,
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error Inesperado"
        )