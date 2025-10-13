from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from DataBase.database import get_db
from DataBase.models import Persona
from schemas import PersonaCreate, PersonaResponse
from utils import calcular_edad
router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
def crear_persona(persona: PersonaCreate, db: Session = Depends(get_db)):
    nueva_persona = Persona(
        nombre=persona.nombre,
        email=persona.email,
        dni=persona.dni,
        telefono=persona.telefono,
        fecha_nacimiento=persona.fecha_nacimiento
    )
    
    edad = calcular_edad(persona.fecha_nacimiento)
    
    
    try:
        db.add(nueva_persona)
        db.commit()
        db.refresh(nueva_persona)
        
    except Exception as e:
        db.rollback()
        
        # Detectar DNI duplicado
        if "UNIQUE constraint failed: personas.dni" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe una persona con DNI {persona.dni}"
            )
        
        # Detectar teléfono duplicado
        elif "UNIQUE constraint failed: personas.telefono" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe una persona con teléfono {persona.telefono}"
            )
        
        # Detectar email duplicado
        elif "UNIQUE constraint failed: personas.email" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe una persona con email {persona.email}"
            )
        
        else:
            raise HTTPException(status_code=500, detail=str(e))

    return {
        "mensaje": "Persona creada correctamente",
        "persona": PersonaResponse(
            id=nueva_persona.id,
            nombre=nueva_persona.nombre,
            email=nueva_persona.email,
            dni=nueva_persona.dni,
            telefono=nueva_persona.telefono,
            fecha_nacimiento=nueva_persona.fecha_nacimiento,
            esta_habilitado=nueva_persona.esta_habilitado,
            edad=edad
        )
    }