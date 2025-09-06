from fastapi import FastAPI, HTTPException
from models import session, Turno

app = FastAPI()

# Obtener un turno en particular
@app.get("/turnos/{id}")
def obtener_turno_particular(id: int):
 turno = session.query(Turno).filter(Turno.id == id).first() 
 if turno is None:
     raise HTTPException(status_code=404, detail="Turno no encontrado")

 return {
  "id": turno.id,
  "fecha": turno.fecha,
  "hora": turno.hora,
  "estado": turno.estado,
  "persona": {
            "id": turno.persona.id,
            "nombre": turno.persona.nombre,
            "email": turno.persona.email,
            "dni": turno.persona.dni,
            "telefono": turno.persona.telefono,
            "fecha_nacimiento": turno.persona.fecha_nacimiento,
            "edad": turno.persona.edad,
        } if turno.persona else None
}