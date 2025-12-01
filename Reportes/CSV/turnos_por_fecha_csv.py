from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from DataBase.models import Turno, Persona
from DataBase.database import get_db
from Utils.utils import validar_y_formatear_fecha_especial
import pandas as pd
from fastapi.responses import FileResponse
from pathlib import Path

router = APIRouter()

# Obtener los turnos de una fecha
@router.get("/csv/turnos-por-fecha")
def exportar_turnos_de_una_fecha_csv(fecha: str, db: Session = Depends(get_db)):
    try:
        fecha_formateada = validar_y_formatear_fecha_especial(fecha)
        turnos = db.query(Turno).join(Persona).filter(Turno.fecha == fecha_formateada).all()
        
        # Si no hay turnos en esa fecha
        if not turnos:
            return {"mensaje": f"No se encontraron turnos para la fecha {fecha_formateada}"}
        
        # Diccionario auxiliar para agrupar por persona
        personas_dict = {}
        
        for t in turnos:
            dni = t.persona.dni
            
            # Si la persona no está aún en el diccionario, la agregamos
            if dni not in personas_dict:
                personas_dict[dni] = {
                "Nombre": t.persona.nombre,
                "DNI": dni,
                "Turnos": [] 
                }
                
                # Agregamos el turno a la lista de esa persona
                personas_dict[dni]["Turnos"].append(
                {"ID":t.id,
                "Hora": t.hora.strftime("%H:%M"),
                "Estado": t.estado })
                
                # Aplanar estructura: una fila por turno
                filas = []
                for persona in personas_dict.values():
                    for turno in persona["Turnos"]:
                        filas.append({
                            "Nombre": persona["Nombre"],
                            "DNI": persona["DNI"],
                            "ID Turno": turno["ID"],
                            "Hora": turno["Hora"],
                            "Estado": turno["Estado"]
                        })
                
                # Crear DataFrame con formato tabular limpio
        df = pd.DataFrame(filas)
        
        # Escribir CSV con título en la primera línea
        nombre_archivo = "turnos_por_fecha.csv"

        ruta_carpeta = Path("Reportes/CSV_Generados")
        ruta_carpeta.mkdir(parents=True, exist_ok=True)

        ruta_archivo = ruta_carpeta / nombre_archivo

        with open(ruta_archivo, "w", encoding="utf-8", newline='') as f:
            f.write(f"Turnos para la fecha {fecha_formateada}\n")  # <-- Título
            df.to_csv(f, index=False)
                    
        # Retornar el archivo como descarga
        return FileResponse(
            ruta_archivo,
            media_type="text/csv",
            filename=f"turnos_{fecha_formateada}.csv"
        )
    
    except Exception as e: raise HTTPException(status_code=500, detail=f"Error al obtener los turnos de la fecha {fecha_formateada}: {str(e)}")