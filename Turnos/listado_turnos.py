from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from DataBase.models import Persona, Turno
from DataBase.database import get_db
from Utils.utils import actualizar_turnos_vencidos

router = APIRouter()

# Listado de los turnos en la BD


@router.get("/turnos")
def listado_turnos(db: Session = Depends(get_db)):
    try:
        # Actualizar automáticamente turnos vencidos antes de mostrar la lista
        turnos_confirmados_actualizados = actualizar_turnos_vencidos(db)

        # Traer todas las personas con sus turnos relacionados
        personas = db.query(Persona).all()


        if not personas:
            raise HTTPException(
                status_code=404, detail="No se han encontrado personas en la base de datos")

        lista_personas = []

        for persona in personas:
            # Obtener los turnos de esta persona, ordenados por fecha y hora
            turnos = db.query(Turno).filter(Turno.persona_id == persona.id).order_by(Turno.fecha, Turno.hora).all()

            # Solo agregar si tiene turnos asignados
            if turnos:
                persona_datos = {
                    "id": persona.id,
                    "nombre": persona.nombre,
                    "dni": persona.dni,
                    "telefono": persona.telefono,
                    "turnos": [
                        {
                            "id": turno.id,
                            "fecha": turno.fecha,
                            "hora": turno.hora,
                            "estado": turno.estado,
                        }
                        for turno in turnos
                    ]
                }
                lista_personas.append(persona_datos)

        if not lista_personas:
            raise HTTPException(
                status_code=404, detail="No se han encontrado turnos asignados en la base de datos")

        return lista_personas

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )
