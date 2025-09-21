from pydantic import BaseModel
from datetime import date, time
from typing import Optional

class PersonaCreate(BaseModel):
    nombre: str
    email: str
    dni: str
    telefono: str
    fecha_nacimiento: date
    
    class Config:
        orm_mode = True

class PersonaUpdate(PersonaCreate):
    esta_habilitado: bool
        
class PersonaResponse(BaseModel):
    id: int
    nombre: str
    email: str
    dni: str
    telefono: str
    fecha_nacimiento: date
    esta_habilitado: bool = True
    edad: int
    
    class Config:
        orm_mode = True

class TurnoCreate(BaseModel):
    fecha : date
    hora : time
    persona_id: Optional[int] = None
    
    class Config:
        orm_mode = True

class TurnoResponse(BaseModel):
    id: int
    fecha: date
    hora: time
    estado: str
    persona_id: int
    
    class Config:
        orm_mode = True