from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from Utils.config import ESTADOS_TURNO, CANT_ELEMENTOS_X_PAGINA
from DataBase.models import Turno
from DataBase.database import get_db
from schemas import FechaQuery
import pandas as pd
from io import StringIO
from fastapi.responses import StreamingResponse

router = APIRouter()

@router.get("/csv/turnos-confirmados-periodo")
def exportar_turnos_confirmados_periodo_csv(
    desde: str = Query(..., description="Fecha futura en formato DD-MM-YYYY"), #Consulta obligatoria de la fecha inicial (Recibo un string)
    hasta: Optional[str] = Query(None, description="Fecha futura en formato DD-MM-YYYY"),  #Consulta opcional de la fecha límite
    pag: Optional[int] = Query(1, ge=1, description="Numero de pagina (minimo 1)"), #El predeterminado es 1 aunque no se ponga. ge=1 significa que debe ser mayor o igual a 1
    db: Session = Depends(get_db)  #Inyecta automáticamente una sesión de base de datos
):
    ## Ejemplo de Endpoint: 
    ## /reportes/csv/turnos-confirmados-periodo?desde=20-10-2025&hasta=30-12-2025&pag=2

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


        #Si ningún registro cumple las condiciones, se lanza una excepción
        if not turnosConfirmados:
            raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No se encontraron registros"
                ) 
        
        paginaDeTurnos = (
            turnosConfirmados
            .order_by(Turno.fecha) #Ordeno por fecha de mas antiguo a más reciente
            .offset(CANT_ELEMENTOS_X_PAGINA * (pag-1)) #Offset es la cantidad de elementos salteados antes de mostrar.
            .limit(CANT_ELEMENTOS_X_PAGINA) #Limito la cantidad de registros por su variable
            .all() #Muestra todos los registros bajo estos parámetros
        )

        if not paginaDeTurnos:
            return {"mensaje":f"No hay registros en la página indicada (pag: {pag})"}
    
        
        filas = []

        for t in paginaDeTurnos:
            filas.append({
                "ID Turno": t.id,
                "ID Persona": t.persona_id,
                "Fecha": t.fecha.strftime("%Y/%m/%d"),
                "Hora": t.hora.strftime("%H:%M"),
            })


        df = pd.DataFrame(filas)

        titulo = (
            f"Turnos confirmados desde {desde} hasta {hasta}"
            if hasta
            else f"Turnos confirmados desde {desde} (sin límite)"
        )

        buffer = StringIO()
        buffer.write(f"{titulo}\n")
        buffer.write(f"Pagina: {pag}\n")
        df.to_csv(buffer, index=False, sep=";", encoding="utf-8-sig")
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=turnos_confirmados_{desde}{'_'+ hasta if hasta else ''}.csv"}
        )

    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error Inesperado"
        )