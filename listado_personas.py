from fastapi import FastAPI, HTTPException, Depends
from models import Persona
from database import get_db
from sqlalchemy.orm import Session
from database import get_db

app = FastAPI()

# Listado de las personas en la BD
@app.get("/personas")
def listado_personas(db: Session = Depends(get_db)):
    personas = db.query(Persona).all()
    if not personas:
        raise HTTPException(status_code=404, detail="No se encontraron personas")
    return [vars(persona) for persona in personas]
