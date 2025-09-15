from fastapi import FastAPI, HTTPException, Depends
from models import Persona
from database import session

app = FastAPI()

#Codigo para mostrar una sola persona

@app.get("/personas/{id}")
def obtener_persona(id: int, db=Depends(lambda: session)):
    persona = db.get(Persona, id)
    if persona is None:
        raise HTTPException(status_code=404, detail="La persona no fue encontrada en la base de datos")
    return vars(persona)
