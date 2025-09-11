from fastapi import FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from models import Persona
from schemas import PersonaCreate, PersonaResponse

app = FastAPI()

#Modificar una Persona
@app.put("/personas/{id}", response_model=PersonaResponse) #Usamos el esquema de PersonaResponse
def modificar_persona(id: int, datos_persona: PersonaCreate, db: Session): #Usamos la plantilla PersonaCreate para los datos_persona
   #Guarda en variable "persona" una query que busca a una persona con el mismo id.
    persona = db.query(Persona).filter(Persona.id == id).first()

    #Si la query no devuelve nada, entonces lanza error 404
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona no encontrada"
        )
    
    # Verificar si el DNI nuevo ya existe (si se está cambiando)
    if persona.dni != datos_persona.dni: #Si el anterior dni es distinto al nuevo, es decir, si se está cambiando
        existe_dni = db.query(Persona).filter(Persona.dni == datos_persona.dni).first() #busco el dni nuevo en la db
        if existe_dni: #Si existe en la db, lanzo la excepción
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El DNI ya está registrado"
            )
        
    #Actualizo los datos
    persona.nombre = datos_persona.nombre
    persona.email = datos_persona.email
    persona.dni = datos_persona.dni
    persona.telefono = datos_persona.telefono
    persona.fecha_nacimiento = datos_persona.fecha_nacimiento

    #Intento guardar los cambios
    try:
        db.commit()
        db.refresh(persona)
        return persona
    
    #Si ocurre un error inesperado, lanza error 500
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error Inesperado al actualizar persona"
        )