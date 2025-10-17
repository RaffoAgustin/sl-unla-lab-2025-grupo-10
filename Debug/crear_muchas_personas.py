from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import date, timedelta
import random
from faker import Faker  # 👈 Para generar datos falsos realistas
from DataBase.database import get_db
from DataBase.models import Persona

router = APIRouter()
faker = Faker("es_AR")  # 👈 Datos falsos argentinos

@router.post("/debug/crear-muchas-personas", status_code=status.HTTP_201_CREATED)
def crear_personas_debug(
    cantidad: int = Query(10, ge=1, le=100, description="Cantidad de personas a generar (1–100)"),
    db: Session = Depends(get_db)
):
    """
    Crea múltiples personas falsas para propósitos de depuración.
    Ejemplo de uso:
    POST /debug/crear-personas?cantidad=10
    """
    personas_creadas = []

    for _ in range(cantidad):
        try:
            # Generar datos aleatorios
            nombre = faker.name()
            email = faker.unique.email()
            dni = str(faker.unique.random_int(min=10000000, max=99999999))
            telefono = str(faker.unique.random_int(min=1100000000, max=1199999999))
            fecha_nacimiento = faker.date_of_birth(minimum_age=18, maximum_age=90)

            nueva_persona = Persona(
                nombre=nombre,
                email=email,
                dni=dni,
                telefono=telefono,
                fecha_nacimiento=fecha_nacimiento,
                esta_habilitado=True
            )

            db.add(nueva_persona)
            db.commit()
            db.refresh(nueva_persona)

            personas_creadas.append({
                "id": nueva_persona.id,
                "nombre": nueva_persona.nombre,
                "email": nueva_persona.email,
                "dni": nueva_persona.dni,
                "telefono": nueva_persona.telefono,
                "fecha_nacimiento": str(nueva_persona.fecha_nacimiento)
            })
        except Exception as e:
            db.rollback()
            print("Error al crear persona:", e)

    return {
        "mensaje": f"Se generaron {len(personas_creadas)} personas correctamente.",
        "personas": personas_creadas
    }