from fastapi import FastAPI, HTTPException, status
from models import session, Persona
app = FastAPI()

# Eliminar una persona
@app.delete("/personas/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_persona(id: int):
 persona = Persona.query.get(id)
 # persona = session.get(Persona, id)
 if persona is None:
     raise HTTPException(status_code=404, detail="Persona no encontrada")
 session.delete(persona)
 session.commit()
 return {"detail": "Persona eliminada"}