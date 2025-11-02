from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from DataBase.models import Turno, Persona
from DataBase.database import get_db
from Utils.utils import validar_dni
import pandas as pd

router = APIRouter()

# Obtener los turnos de una fecha
@router.get("/csv/turnos-por-persona")
def turnos_por_persona(
    dni: str = Query(..., description="DNI de 8 dígitos"),
    db: Session = Depends(get_db)
):
    try:
        validar_dni(dni)
        turnos = db.query(Turno).join(Persona).filter(
            Turno.persona_id == Persona.id,
            Persona.dni == dni
        ).all()

        # Si esa persona no tiene turnos:
        if not turnos:
            return {"mensaje": f"No se encontraron turnos para la persona con DNI = {dni}"}

        turnos_persona = [
            {
                "Nombre": t.persona.nombre,
                "ID": t.id,
                "Fecha": t.fecha,
                "Hora": t.hora,
                "Estado": t.estado,
            } for t in turnos
        ]

        df = pd.DataFrame(turnos_persona)

        # Escribir CSV con título en la primera línea
        nombre_archivo = "turnos_por_persona.csv"
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write(f"Turnos para la persona con DNI {dni}\n")  # <-- Título
            df.to_csv(f, index=False)

        # Retornar mensaje con nombre de archivo y lista de turnos
        return {
            "mensaje": f"CSV generado correctamente para {turnos[0].persona.nombre}",
            "archivo": nombre_archivo,
            "turnos": turnos_persona
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener los turnos de la persona con DNI = {dni}: {str(e)}"
        )
