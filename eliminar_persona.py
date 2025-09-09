from fastapi import FastAPI, HTTPException, status
from models import Persona
from database import session
app = FastAPI()

# Eliminar una persona
@app.delete("/personas/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_persona(id: int):
    try:
        persona = session.get(Persona, id)
        if persona is None:
            raise HTTPException(status_code=404, detail="Persona no encontrada")
        session.delete(persona)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Error al eliminar la persona")