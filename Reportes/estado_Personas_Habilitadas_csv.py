from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
import pandas as pd

from DataBase.database import get_db
from DataBase.models import Persona
from Utils.utils import calcular_edad

router = APIRouter()

@router.get("/csv/estado-personas")
def exportar_estado_personas_csv(
    habilitada: bool = Query(..., description="true o false"),
    db: Session = Depends(get_db)
):
    try:
        personas = db.query(Persona).filter(
            Persona.esta_habilitado == habilitada
        ).all()

        if not personas:
            return {"mensaje": f"No se encontraron personas con habilitada={habilitada}"}

        filas = []

        for p in personas:
            filas.append({
                "ID": p.id,
                "Nombre": p.nombre,
                "Email": p.email,
                "DNI": p.dni,
                "Telefono": p.telefono,
                "Fecha nacimiento": str(p.fecha_nacimiento),
                "Edad": calcular_edad(p.fecha_nacimiento),
                "Habilitada": p.esta_habilitado
            })

        df = pd.DataFrame(filas)

        nombre_archivo = "estado_personas.csv"

        with open(nombre_archivo, "w", encoding="utf-8", newline='') as f:
            titulo = f"Personas con habilitada={habilitada}\n"
            f.write(titulo)
            df.to_csv(f, index=False)

        return FileResponse(
            nombre_archivo,
            media_type="text/csv",
            filename=f"estado_personas_{habilitada}.csv"
        )

    except Exception as e:
        print("Error en /csv/estado-personas:", str(e))
        raise HTTPException(status_code=500, detail="Error interno del servidor")