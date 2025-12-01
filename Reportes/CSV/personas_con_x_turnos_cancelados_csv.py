from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from Utils.config import ESTADOS_TURNO
from DataBase.models import Turno, Persona
from DataBase.database import get_db
from pathlib import Path
from fastapi.responses import FileResponse
from Utils.utils import calcular_edad
from pathlib import Path
from fastapi.responses import FileResponse
import pandas as pd

router = APIRouter()

@router.get("/csv/turnos-cancelados-minimo")
def exportar_personas_con_turnos_cancelados_csv(
    min: int = Query(..., description="Minimo de turnos cancelados"), #Pide al usuario el mínimo de Turnos cancelados (... significa obligatorio)
    db: Session = Depends(get_db)  #Inyecta automáticamente una sesión de base de datos
):
    try:
        if min <= 0:
                raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El valor minimo no puede ser negativo o 0"
        )
        
        personas=(
                db.query(Persona) #Hace una consulta de personas
                .join(Turno) #Junto a sus turnos
                .filter(Turno.estado == ESTADOS_TURNO[1]) #Tomo unicamente a los turnos cancelados
                .group_by(Persona.id) #Agrupo a las personas según su id, necesario para que las func funcionen correctamente
                .having(func.count(Turno.id) >= min) #Filtro los grupos (cada persona) donde la cantidad de turnos (ya filtrados) sean mayores al minimo
                .all() #Muestro todas las personas con estas condiciones
            )

        filas = []

        for p in personas:
            filas.append({
                "ID": p.id,
                "Nombre": p.nombre,
                "Email": p.email,
                "DNI": p.dni,
                "Telefono": p.telefono,
                "Fecha nacimiento": str(p.fecha_nacimiento),
                "Edad": calcular_edad(p.fecha_nacimiento),
                "Habilitada": p.esta_habilitado
            })

        df = pd.DataFrame(filas)

        nombre_archivo = f"turnos_cancelados_min_{min}.csv"
    
        # Carpeta de salida
        ruta_carpeta = Path("Reportes/CSV_Generados")
        ruta_carpeta.mkdir(parents=True, exist_ok=True)

        ruta_archivo = ruta_carpeta / nombre_archivo

        with open(ruta_archivo, "w", encoding="utf-8", newline='') as f:
            f.write(f"Personas con {min} turno/s cancelados o más\n")
            df.to_csv(f, index=False)

        return FileResponse(
            ruta_archivo,
            media_type="text/csv",
            filename=nombre_archivo
        )
    
    except Exception as e:
        print("Error en el reporte de turnos cancelados:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error Inesperado al obtener el reporte"
        )