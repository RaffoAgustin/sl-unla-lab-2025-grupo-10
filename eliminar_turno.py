from fastapi import FastAPI, HTTPException, status
from models import session, Turno

app = FastAPI()

# Eliminar un turno
@app.delete("/turnos/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_turno(id: int):
 turno = Turno.query.get(id) 
 # turno = session.get(Turno, id)
 if turno is None:
     raise HTTPException(status_code=404, detail="Turno no encontrado")
 session.delete(turno)
 session.commit()
 return {"detail": "Turno eliminado"}