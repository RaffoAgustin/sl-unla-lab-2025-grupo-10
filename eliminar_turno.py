from fastapi import FastAPI, HTTPException, status
from models import Turno
from database import session

app = FastAPI()

# Eliminar un turno
@app.delete("/turnos/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_turno(id: int):
    try:
        turno = session.get(Turno, id)
        if turno is None:
            raise HTTPException(status_code=404, detail="Turno no encontrado")
        session.delete(turno)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Error al eliminar el turno")