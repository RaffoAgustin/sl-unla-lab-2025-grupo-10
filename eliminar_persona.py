from fastapi import FastAPI, HTTPException, status, Depends
from models import Persona
from sqlalchemy.orm import Session
from database import get_db

app = FastAPI()

# Eliminar una persona
@app.delete("/personas/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_persona(id: int, db: Session = Depends(get_db)):
    try:
        persona = db.get(Persona, id)
        if persona is None:
            raise HTTPException(status_code=404, detail="Persona no encontrada")
        db.delete(persona)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al eliminar la persona")