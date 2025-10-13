from pydantic import BaseModel, validator, EmailStr
import re
from datetime import datetime, date, time
from typing import Optional
from utils import es_horario_valido

class PersonaCreate(BaseModel):
    nombre: str
    email: EmailStr # Validación automática de email
    dni: str
    telefono: str
    fecha_nacimiento: date
    
    class Config:
        orm_mode = True
    
    @validator("nombre") # se indica el nombre del campo a validar
    def validar_nombre(cls, v): # cls (la clase) y valor (el valor del campo a validar).
        if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$", v):
            raise ValueError("El nombre solo puede contener letras y espacios")
        if not (3 <= len(v) <= 15):
            raise ValueError("El nombre debe tener entre 3 y 15 caracteres")
        return v
    
    @validator("dni")
    def validar_dni(cls, v):
        if not re.fullmatch(r"\d{8}", v): # Asegura que solo haya 8 dígitos y nada más.
            raise ValueError("El DNI debe contener exactamente 8 números")
        return v
    
    @validator("telefono")
    def validar_telefono(cls, v):
        if not re.fullmatch(r"\d{10}", v): # Asegura que solo haya 10 dígitos y nada más.
            raise ValueError("El teléfono debe contener exactamente 10 números")
        return v
    
    @validator("fecha_nacimiento", pre=True)
    def validar_fecha(cls, v):
        if isinstance(v, str):
            # Validar que solo contenga números y - o /
            if not re.fullmatch(r"[0-9/-]+", v):
                raise ValueError("La fecha solo puede contener números, '-' o '/'")
            
            # Si viene como string, intentar parsear distintos formatos
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
                try:
                    v = datetime.strptime(v, fmt).date()
                    break
                except ValueError:
                    continue
            else:
                raise ValueError("Formato de fecha no válido. Usa YYYY-MM-DD o DD/MM/YYYY.")
        
        # Validar que no sea una fecha futura
        if v > date.today():
            raise ValueError("La fecha de nacimiento no puede ser futura")
        
        return v

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
    
    @validator("fecha", pre=True)
    def validar_fecha_turno(cls, v):
        if isinstance(v, str):
            # Validar que solo contenga números, - o /
            if not re.fullmatch(r"[0-9/-]+", v):
                raise ValueError("La fecha solo puede contener números, '-' o '/'")
            
            # Intentar parsear distintos formatos
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
                try:
                    v = datetime.strptime(v, fmt).date()
                    break
                except ValueError:
                    continue
            else:
                raise ValueError("Formato de fecha no válido. Usa YYYY-MM-DD o DD/MM/YYYY.")
        
        # Validar que no sea pasada
        if v < date.today():
            raise ValueError("La fecha del turno no puede ser pasada")
        
        return v
        
    @validator("hora", pre=True)
    def validar_hora(cls, v):
        if isinstance(v, str):
            # Validar que solo contenga números y ':'
            if not re.fullmatch(r"[0-9:]+", v):
                raise ValueError("La hora solo puede contener números y ':'")
            
            # Intentar parsear los formatos permitidos
            for fmt in ("%H:%M:%S", "%H:%M"):
                try:
                    v = datetime.strptime(v, fmt).time()
                    break
                except ValueError:
                    continue
            else:
                raise ValueError("Formato de hora no válido. Usa HH:MM o HH:MM:SS.")
        
        # Validar contra la lista de horarios permitidos
        if not es_horario_valido(v):
            raise ValueError("La hora del turno no está en los horarios permitidos")
        
        return v

class FechaQuery(BaseModel):
    fecha: date
    
    @validator("fecha", pre=True)
    def validar_fecha_turno(cls, v):
        if isinstance(v, str):
            # Validar que solo contenga números, - o /
            if not re.fullmatch(r"[0-9/-]+", v):
                raise ValueError("La fecha solo puede contener números, '-' o '/'")
            
            # Intentar parsear distintos formatos
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
                try:
                    v = datetime.strptime(v, fmt).date()
                    break
                except ValueError:
                    continue
            else:
                raise ValueError("Formato de fecha no válido. Usa YYYY-MM-DD o DD/MM/YYYY.")
        
        # Validar que no sea pasada
        if v < date.today():
            raise ValueError("La fecha del turno no puede ser pasada")
        
        return v
    
class TurnoResponse(BaseModel):
    id: int
    fecha: date
    hora: time
    estado: str
    persona_id: int
    
    class Config:
        orm_mode = True