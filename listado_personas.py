from fastapi import FastAPI, HTTPException, Depends
from models import Persona
from database import session

app = FastAPI()

# Listado de las personas en la BD
@app.get("/personas")
def listado_personas(db: Session = Depends(get_db)):
    personas = db.query(Persona).all()
    if not personas:
        raise HTTPException(status_code=404, detail="No se encontraron personas")
    return [vars(persona) for persona in personas]
