from fastapi import FastAPI, HTTPException, status, Depends
from models import Turno
from sqlalchemy.orm import Session
from database import get_db

app = FastAPI()

# Eliminar un turno
@app.delete("/turnos/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_turno(id: int, db: Session = Depends(get_db)):
    try:
        turno = db.get(Turno, id)
        if turno is None:
            raise HTTPException(status_code=404, detail="Turno no encontrado")
        db.delete(turno)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al eliminar el turno")