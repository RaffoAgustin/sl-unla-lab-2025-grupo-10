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

        # Usar LEFT JOIN para incluir turnos sin persona asignada (cancelados)
        resultados = db.query(Turno, Persona).outerjoin(
            Persona).order_by(Turno.fecha, Turno.hora).all()

        if not resultados:
            raise HTTPException(
                status_code=404, detail="No se han encontrado turnos en la base de datos")

        lista_turnos = []
        for turno, persona in resultados:
            turno_datos = {
                "id": turno.id,
                "fecha": turno.fecha,
                "hora": turno.hora,
                "estado": turno.estado,
            }

            # Solo agregar datos de persona si existe (no es null)
            if persona:
                turno_datos["persona"] = {
                    "id": persona.id,
                    "nombre": persona.nombre,
                    "dni": persona.dni,
                    "telefono": persona.telefono
                }
            else:
                # Turno sin persona asignada (cancelado o disponible)
                turno_datos["persona"] = None

            lista_turnos.append(turno_datos)

        return lista_turnos

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )
