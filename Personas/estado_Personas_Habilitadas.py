from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import HTTPException
from sqlalchemy.orm import Session
from DataBase.database import get_db
from DataBase.models import Persona
from schemas import PersonaResponse
from Utils.utils import calcular_edad

router = APIRouter()

@router.get("/estado-personas")
def estado_personas(
    habilitada: bool = Query(..., description="true o false"),
    db: Session = Depends(get_db)
):
    try:
        personas = db.query(Persona).filter(
            Persona.esta_habilitado == habilitada
        ).all()

        if not personas:
            return {
                "habilitada": habilitada,
                "cantidad": 0,
                "personas": []
            }

        resultado = []
        for p in personas:
            edad = calcular_edad(p.fecha_nacimiento)
            persona_resp = PersonaResponse(
                id=p.id,
                nombre=p.nombre,
                email=p.email,
                dni=p.dni,
                telefono=p.telefono,
                fecha_nacimiento=p.fecha_nacimiento,
                esta_habilitado=p.esta_habilitado,
                edad=edad
            )
            resultado.append(persona_resp)

        return {
            "habilitada": habilitada,
            "cantidad": len(resultado),
            "personas": resultado
        }

    except Exception as e:
        print("Error en /estado-personas:", str(e))
        raise HTTPException(status_code=500, detail="Error interno del servidor")