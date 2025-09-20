from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import date
from models import Turno
from database import get_db

app = FastAPI()

@app.get("/turnos-disponibles")
def turnos_disponibles(
    fecha: date = Query(..., description="Fecha en formato YYYY-MM-DD"), #Pide al usuario un elemento date (... significa obligatorio)
    db: Session = Depends(get_db)  #Inyecta automáticamente una sesión de base de datos
):
    try:
        #Generar horarios base (De 9 a 17 en intervalos de media hora)
        #TODO: Hacer una función auxiliar que te devuelva esta lista, en lugar de hardcodearla
        horarios_base = ["09:00", "09:30", "10:00", "10:30", 
                        "11:00", "11:30", "12:00", "12:30", 
                        "13:00", "13:30", "14:00", "14:30", 
                        "15:00", "15:30","16:00", "16:30"]

        #Hago una consulta de los turnos donde le fecha sea la misma a la pedida por el usuario
        turnos_ocupados = (db.query(Turno).filter(Turno.fecha == fecha).all())

        #Guardo las horas que ocupan esos turnos en un set, lo que evita repeticiones
        #Utilizo el método .strftime() para convertir t.hora en un string, ya que sino devolvería un objeto (datetime.time(14, 30))
        horas_ocupadas = {t.hora.strftime("%H:%M") for t in turnos_ocupados}

        #Filtrar horarios disponibles
        horarios_disponibles = [h #Guarda la variable h (hora)
                                for h in horarios_base #A partir de la lista horarios_base
                                if h not in horas_ocupadas] #Donde la hora guardada no está ocupada
        
        return {
            "fecha": fecha.strftime("%Y-%m-%d"), #Convierte nuevamente el objeto "fecha" a string
            "horarios_disponibles": horarios_disponibles #Devuelve la lista de horarios disponibles
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error Inesperado"
        )