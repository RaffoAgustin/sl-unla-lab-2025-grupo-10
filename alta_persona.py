from fastapi import FastAPI, HTTPException, status
from models import Persona
app = FastAPI()

# Crear una nueva persona
@app.post("/personas", status_code=status.HTTP_201_CREATED)
def crear_persona(datos_persona, db):
    persona_nueva = Persona(
        nombre=datos_persona.nombre,
        email=datos_persona.email,
        dni=datos_persona.dni,
        telefono=datos_persona.telefono,
        fecha_nacimiento=datos_persona.fecha_nacimiento,
        edad=datos_persona.edad,
        esta_habilitado=datos_persona.esta_habilitado
    )
    
    db.add(persona_nueva)
    try:
        db.commit()
        db.refresh(persona_nueva)
    except:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail="Error al crear persona (email duplicado o datos inválidos)"
        )
    
    return vars(persona_nueva)
