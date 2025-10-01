from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from DataBase.models import Persona, Turno
from DataBase.database import get_db

router = APIRouter()

# Listado de los turnos en la BD
@router.get("/turnos")
def listado_turnos(db: Session = Depends(get_db)):
    turnos = db.query(Turno).all()
    if not turnos:
        raise HTTPException(status_code=404, detail="No se han encontrado turnos en la base de datos")

    resultado = []  # Lista para almacenar los turnos con detalles de la persona
    for turno in turnos:
        persona = db.query(Persona).filter(Persona.id == turno.persona_id).first()
        turno_info = {
            "ID Turno": turno.id,
            "Fecha": turno.fecha,
            "Hora": str(turno.hora),
            "Estado": turno.estado,
            "Persona": {
                "ID Persona": persona.id,
                "Nombre": persona.nombre,
                "Email": persona.email
            } if persona else None
        }
        resultado.append(turno_info)
    
    return resultado