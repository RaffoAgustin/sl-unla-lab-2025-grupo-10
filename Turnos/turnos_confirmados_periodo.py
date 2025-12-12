from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from Utils.config import ESTADOS_TURNO, CANT_ELEMENTOS_X_PAGINA
from DataBase.models import Turno
from DataBase.database import get_db
from schemas import FechaQuery

router = APIRouter()

@router.get("/turnos-confirmados-periodo")
def turnos_confirmados_periodo(
    desde: str = Query(..., description="Fecha futura en formato DD-MM-YYYY"), #Consulta obligatoria de la fecha inicial (Recibo un string)
    hasta: Optional[str] = Query(None, description="Fecha futura en formato DD-MM-YYYY"),  #Consulta opcional de la fecha límite
    pag: Optional[int] = Query(1, ge=1, description="Numero de pagina (minimo 1)"), #El predeterminado es 1 aunque no se ponga. ge=1 significa que debe ser mayor o igual a 1
    db: Session = Depends(get_db)  #Inyecta automáticamente una sesión de base de datos
):
    ## Ejemplo de Endpoint: 
    ## /reportes/turnos-confirmados-periodo?desde=20-10-2025&hasta=30-12-2025&pag=3

    try:
        # Convierto el string "desde" a un objeto date a través de la clase FechaQuery y sus validaciones
        fecha_desde = FechaQuery(fecha=desde).fecha 
                                #     ^ Recibe a "desde" como parámetro

        # Validar fecha hasta si existe
        fecha_hasta = None #Inicializo la variable
        if hasta:
            fecha_hasta = FechaQuery(fecha=hasta).fecha #Hago lo mismo que con "desde"
            if fecha_hasta < fecha_desde:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La fecha 'hasta' no puede ser anterior a la fecha 'desde'"
                )

        #Consulta inicial
        turnosConfirmados = (
            db.query(Turno)
            .filter(
                Turno.estado == ESTADOS_TURNO.Confirmado, #Aquellos turnos confirmados
                Turno.fecha >= fecha_desde) #Donde su fecha sea mas reciente que "desde"
                )
        
        if hasta: #Si "hasta" fue indicado...
            turnosConfirmados = turnosConfirmados.filter(Turno.fecha <= fecha_hasta) #...También filtro por las fechas más viejas que "hasta"

        #Guardo la cantidad de turnos totales encontrados en una variable para devolverla más adelante
        turnosConfirmadosTotales = turnosConfirmados.count()

        paginaDeTurnos = (
            turnosConfirmados
            .order_by(Turno.fecha) #Ordeno por fecha de mas antiguo a más reciente
            .offset(CANT_ELEMENTOS_X_PAGINA * (pag-1)) #Offset es la cantidad de elementos salteados antes de mostrar.
            .limit(CANT_ELEMENTOS_X_PAGINA) #Limito la cantidad de registros por su variable
            .all() #Muestra todos los registros bajo estos parámetros
        )

        return {
            "pagina": pag,
            "turnosConfirmadosTotales": turnosConfirmadosTotales,
            "cantElementosPagActual": len(paginaDeTurnos),
            "turnos":  "No se encontraron turnos en el periodo indicado" if turnosConfirmadosTotales == 0
                        else paginaDeTurnos 
                        or "No se encontraron turnos en la página indicada" 
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error Inesperado"
        )