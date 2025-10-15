from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from DataBase.models import Persona
from DataBase.database import get_db
from schemas import PersonaResponse
from Utils.utils import calcular_edad

router = APIRouter()

# Listado de las personas en la BD


@router.get("/personas")
def listado_personas(db: Session = Depends(get_db)):
    try:
        personas = db.query(Persona).all()
        if not personas:
            raise HTTPException(
                status_code=404, detail="No se encontraron personas")

        # Crear lista con PersonaResponse incluyendo la edad calculada
        lista_personas= []
        for persona in personas:
            edad = calcular_edad(persona.fecha_nacimiento)
            persona_response = PersonaResponse(
                id=persona.id,
                nombre=persona.nombre,
                email=persona.email,
                dni=persona.dni,
                telefono=persona.telefono,
                fecha_nacimiento=persona.fecha_nacimiento,
                esta_habilitado=persona.esta_habilitado,
                edad=edad
            )
            lista_personas.append(persona_response)

        return lista_personas

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )
