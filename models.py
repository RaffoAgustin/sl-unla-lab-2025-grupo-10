# models.py
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, Time, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import date

engine = create_engine('sqlite:///mi_base.db', echo=True)
Base = declarative_base()

class Persona(Base):
    __tablename__ = "personas"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, nullable=False)
    dni = Column(String, unique=True, nullable=False)
    telefono = Column(String, nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    esta_habilitado = Column(Boolean, default=True, nullable=False)
    
    @property
    def edad(self):
        """Calcula la edad automáticamente según fecha de nacimiento."""
        today = date.today()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )
        