from sqlalchemy import Column, Integer, String, Boolean, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Persona(Base):
    __tablename__ = "personas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, nullable=False)
    dni = Column(String, unique=True, nullable=False)
    telefono = Column(String, nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    esta_habilitado = Column(Boolean, default=True, nullable=False)


class Turno(Base):
    __tablename__ = "turnos"
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)
    estado = Column(String, default="Pendiente", nullable=False)
    
    # Relación con Persona
    persona_id = Column(Integer, ForeignKey("personas.id"), nullable=True)
    persona = relationship("Persona", backref="turnos") 
