from pydantic import BaseModel
from datetime import date, time

class Persona(BaseModel):
    nombre: str
    email: str
    dni: str
    telefono: str
    fecha_nacimiento: date
    esta_habilitado: bool = True
    edad: int | None = None
    
    class Config:
        orm_mode = True

class Turno(BaseModel):
    fecha = date
    hora = time
    estado: str = "Pendiente"
    persona_id: int
    
    
    # Relación con Persona
    persona_id = Column(Integer, ForeignKey("personas.id"), nullable=False)
    persona = relationship("Persona", backref="turnos")