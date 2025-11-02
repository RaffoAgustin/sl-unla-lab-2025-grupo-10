from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from DataBase.models import Turno, Persona
from DataBase.database import get_db
from Utils.utils import validar_y_formatear_fecha_especial

router = APIRouter()
    
# Obtener los turnos de una fecha
@router.get("/turnos-por-fecha")
def obtener_turnos_de_una_fecha(
    fecha: str,
    db: Session = Depends(get_db)  #Inyecta automáticamente una sesión de base de datos
):
    
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
            personas_dict[dni]["Turnos"].append({
                "Hora": t.hora,
                "Estado": t.estado
            })

        # Convertimos el diccionario en una lista para devolverlo
        personas_lista = list(personas_dict.values())

        # Retornamos el resultado agrupado
        return {
            "Fecha": fecha_formateada,
            "Personas": personas_lista
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener los turnos de la fecha {fecha_formateada}: {str(e)}")
