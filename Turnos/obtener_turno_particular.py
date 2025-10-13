from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from DataBase.models import Turno, Persona
from DataBase.database import get_db
from utils import calcular_edad

router = APIRouter()

# Obtener un turno en particular
@router.get("/turnos/{id}")
def obtener_turno_particular(id: int, db: Session = Depends(get_db)):
    try:
        turno = db.get(Turno, id)
        if turno is None:
            raise HTTPException(status_code=404, detail=f"Turno con ID {id} no encontrado")
        
        persona = db.get(Persona, turno.persona_id)

        return {
                "id": turno.id,
                "fecha": turno.fecha,
                "hora": turno.hora,
                "estado": turno.estado,
                "persona": {
                    "id": persona.id,
                    "nombre": persona.nombre,
                    "email": persona.email,
                    "dni": persona.dni,
                    "telefono": persona.telefono,
                    "fecha_nacimiento": persona.fecha_nacimiento,
                    "esta_habilitado": persona.esta_habilitado,
                    "edad": calcular_edad(persona.fecha_nacimiento)
                } if persona else None
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener el turno con ID {id}: {str(e)}")