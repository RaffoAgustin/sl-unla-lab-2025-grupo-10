from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import date, timedelta
import random
from DataBase.database import get_db
from DataBase.models import Turno, Persona
from Utils.config import HORARIOS_VALIDOS

router = APIRouter()

@router.post("/debug/crear-muchos-turnos", status_code=status.HTTP_201_CREATED)
def crear_turnos_debug(
    cantidad: int = Query(10, ge=1, le=200, description="Cantidad de turnos a generar"),
    dias_futuros: int = Query(30, ge=0, le=365, description="Rango máximo de días a futuro para los turnos"),
    db: Session = Depends(get_db)
):
    """
    Crea múltiples turnos falsos asignados a personas habilitadas.
    Ejemplo: POST /debug/crear-muchos-turnos?cantidad=20&dias_futuros=60
    """

    personas_habilitadas = db.query(Persona).filter(Persona.esta_habilitado == True).all()
    if not personas_habilitadas:
        raise HTTPException(status_code=400, detail="No hay personas habilitadas en la base de datos")

    turnos_creados = []
    fechas_generadas = set()

    for _ in range(cantidad):
        try:
            persona = random.choice(personas_habilitadas)
            
            # Generar una fecha aleatoria dentro del rango
            fecha_turno = date.today() + timedelta(days=random.randint(0, dias_futuros))
            hora_turno = random.choice(HORARIOS_VALIDOS)
            clave_turno = (fecha_turno, hora_turno)

            # Evitar duplicados
            if clave_turno in fechas_generadas:
                continue
            fechas_generadas.add(clave_turno)

            # Evitar conflictos en DB
            ocupado = db.query(Turno).filter(
                Turno.fecha == fecha_turno,
                Turno.hora == hora_turno
            ).first()
            if ocupado:
                continue

            turno = Turno(
                fecha=fecha_turno,
                hora=hora_turno,
                estado="Pendiente",
                persona_id=persona.id
            )

            db.add(turno)
            db.commit()
            db.refresh(turno)

            turnos_creados.append({
                "id": turno.id,
                "fecha": str(turno.fecha),
                "hora": str(turno.hora),
                "estado": turno.estado,
                "persona_id": persona.id,
                "persona_nombre": persona.nombre
            })

        except Exception as e:
            db.rollback()
            print(f"Error al crear turno: {e}")

    return {
        "mensaje": f"Se generaron {len(turnos_creados)} turnos correctamente.",
        "turnos": turnos_creados
    }
