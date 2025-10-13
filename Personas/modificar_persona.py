from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from DataBase.models import Persona
from DataBase.database import get_db
from schemas import PersonaUpdate
from datetime import date
from utils import calcular_edad

router = APIRouter()

#Modificar una Persona
@router.put("/personas/{id}")
def modificar_persona(
    id: int, 
    datos_persona: PersonaUpdate,  #Usamos la plantilla PersonaUpdate para los datos_persona
    db: Session=Depends(get_db) #Inyecta automáticamente una sesión de base de datos
    ):

   #Guarda en variable "persona" una persona con el mismo id del db.
    persona = db.get(Persona, id)

    #Si no encuentra a la persona, entonces lanza error 404
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
    persona.esta_habilitado = datos_persona.esta_habilitado
    edad = calcular_edad(persona.fecha_nacimiento)


    #Intento guardar los cambios
    try:
        db.commit()
        db.refresh(persona)
        return {
            "mensaje": f"Persona con ID {id} actualizada correctamente",
            "persona":{
                    "id": persona.id,
                    "nombre": persona.nombre,
                    "email": persona.email,
                    "dni": persona.dni,
                    "telefono": persona.telefono,
                    "fecha_nacimiento": persona.fecha_nacimiento,
                    "edad": edad,
                    "esta_habilitado": persona.esta_habilitado
            }
        }
    
    #Si ocurre un error inesperado, lanza error 500
    except Exception as e:
        db.rollback()
        print("Error al actualizar persona:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error Inesperado al actualizar persona"
        )