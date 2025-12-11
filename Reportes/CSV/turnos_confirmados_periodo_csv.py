from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from Utils.config import ESTADOS_TURNO, CANT_ELEMENTOS_X_PAGINA
from DataBase.models import Turno
from DataBase.database import get_db
from schemas import FechaQuery
from pathlib import Path
from fastapi.responses import FileResponse
import pandas as pd

router = APIRouter()

@router.get("/csv/turnos-confirmados-periodo")
def exportar_turnos_confirmados_periodo_csv(
    desde: str = Query(..., description="Fecha futura en formato DD-MM-YYYY"), #Consulta obligatoria de la fecha inicial (Recibo un string)
    hasta: Optional[str] = Query(None, description="Fecha futura en formato DD-MM-YYYY"),  #Consulta opcional de la fecha límite
    #La paginación no es necesaria, supongo
    db: Session = Depends(get_db)  #Inyecta automáticamente una sesión de base de datos
):
    ## Ejemplo de Endpoint: 
    ## /reportes/pdf/turnos-confirmados-periodo?desde=20-10-2025&hasta=30-12-2025

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


        turnosListos = turnosConfirmados.all()

        #Si ningún registro cumple las condiciones, se lanza una excepción
        if not turnosListos:
            raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No se encontraron registros"
                )
        
        filas = []

        for t in turnosListos:
            filas.append({
                "ID": t.id,
                "Persona ID": t.persona_id,
                "Fecha": str(t.fecha),
                "Hora": str(t.hora),
                "Estado": t.estado
            })

        df = pd.DataFrame(filas)

        nombre_archivo = f"turnos_confirmados_{desde}{'_'+ hasta if hasta else ''}.csv"

        titulo = (
            f"Turnos confirmados desde {desde} hasta {hasta}"
            if hasta
            else f"Turnos confirmados desde {desde} (sin límite)"
        )
    
        # Carpeta de salida
        ruta_carpeta = Path("Reportes/CSV_Generados")
        ruta_carpeta.mkdir(parents=True, exist_ok=True)

        ruta_archivo = ruta_carpeta / nombre_archivo

        with open(ruta_archivo, "w", encoding="utf-8", newline='') as f:
            f.write(f"{titulo}\n")
            df.to_csv(f, index=False)

        return FileResponse(
            ruta_archivo,
            media_type="text/csv",
            filename=nombre_archivo
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error Inesperado"
        )