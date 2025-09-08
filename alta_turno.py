from fastapi import FastAPI, HTTPException, status
from models import Turno
app = FastAPI()

# Crear una nuevo Turno
@app.post("/turno", status_code=status.HTTP_201_CREATED)
def crear_turno(datos_turno, db):
    turno_nuevo = Turno(
        fecha=datos_turno.fecha,
        hora=datos_turno.hora,
        estado=datos_turno.estado,
        persona_id=datos_turno.persona_id
    )
    
    db.add(turno_nuevo)
    try:
        db.commit()
        db.refresh(turno_nuevo)
    except:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail="Error al crear un nuevo Turno (Datos inválidos)"
        )
    
    return vars(turno_nuevo)