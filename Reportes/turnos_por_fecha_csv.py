from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from DataBase.models import Turno, Persona
from DataBase.database import get_db
from Utils.utils import validar_y_formatear_fecha_especial
import pandas as pd

router = APIRouter()

# Obtener los turnos de una fecha
@router.get("/csv/turnos-por-fecha")
def obtener_turnos_de_una_fecha(fecha: str, db: Session = Depends(get_db)):
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
                personas_dict[dni] = { "Nombre": t.persona.nombre,
                                      "DNI": dni,
                                      "Turnos": [] 
                }
                
                # Agregamos el turno a la lista de esa persona
                personas_dict[dni]["Turnos"].append({ "Hora": t.hora.strftime("%H:%M"), "Estado": t.estado })
                
                # Convertimos el diccionario en una lista para devolverlo
                personas_lista = list(personas_dict.values())
                
                df = pd.DataFrame(personas_lista)
                
                # Escribir CSV con título en la primera línea
                nombre_archivo = "turnos_por_fecha.csv"
                with open(nombre_archivo, "w", encoding="utf-8") as f:
                    f.write(f"Turnos para la fecha {fecha_formateada}\n")  # <-- Título
                    df.to_csv(f, index=False) 
                    
                # Retornar mensaje con nombre de archivo y lista de turnos
            return { "archivo": nombre_archivo, "turnos": personas_lista }
    
    except Exception as e: raise HTTPException(status_code=500, detail=f"Error al obtener los turnos de la fecha {fecha_formateada}: {str(e)}")