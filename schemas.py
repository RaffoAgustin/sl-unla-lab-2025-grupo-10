from pydantic import BaseModel, field_validator, EmailStr
from datetime import date, time
from typing import Optional
import re
from variables import HORARIOS_VALIDOS

class PersonaCreate(BaseModel):
    nombre: str
    email: EmailStr
    dni: str
    telefono: str
    fecha_nacimiento: date

    class Config:
        from_attributes = True

    @field_validator("nombre")
    def validar_nombre(cls, v: str):
        if not re.match(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$", v):
            raise ValueError("El nombre solo puede contener letras y espacios")
        if not (3 <= len(v) <= 15):
            raise ValueError("El nombre debe tener entre 3 y 15 caracteres")
        return v

    @field_validator("dni")
    def validar_dni(cls, v: str):
        if not re.fullmatch(r"\d{8}", v):
            raise ValueError("El DNI debe contener exactamente 8 números")
        return v

    @field_validator("telefono")
    def validar_telefono(cls, v: str):
        if not re.fullmatch(r"\d{10}", v):
            raise ValueError("El teléfono debe contener exactamente 10 números")
        return v

    @field_validator("fecha_nacimiento")
    def validar_fecha_nacimiento(cls, v: date):
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
        from_attributes = True


class TurnoCreate(BaseModel):
    fecha: date
    hora: time
    persona_id: Optional[int] = None

    class Config:
        from_attributes = True

    @field_validator("fecha")
    def validar_fecha_turno(cls, v: date):
        if v < date.today():
            raise ValueError("La fecha del turno no puede ser pasada")
        return v

    @field_validator("hora")
    def validar_hora(cls, v: time):
        if v not in HORARIOS_VALIDOS:
            raise ValueError("La hora del turno no está en los horarios permitidos")
        return v


class FechaQuery(BaseModel):
    fecha: date

    @field_validator("fecha")
    def validar_fecha_query(cls, v: date):
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
        from_attributes = True
