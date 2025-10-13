from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from DataBase.models import Persona, Turno
from DataBase.database import get_db

router = APIRouter()

# Listado de los turnos en la BD


@router.get("/turnos")
def listado_turnos(db: Session = Depends(get_db)):
    try:
        resultados = db.query(Turno, Persona).join(
            Persona).order_by(Turno.fecha, Turno.hora).all()

        if not resultados:
            raise HTTPException(
                status_code=404, detail="No se han encontrado turnos en la base de datos")

        lista_turnos = []
        for turno, persona in resultados:
            lista_turnos.append({
                "id": turno.id,
                "fecha": turno.fecha,
                "hora": turno.hora,
                "estado": turno.estado,
                "persona": {
                    "id": persona.id,
                    "nombre": persona.nombre,
                    "dni": persona.dni,
                    "telefono": persona.telefono
                }
            })

        return lista_turnos

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )
