from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from DataBase.database import get_db
from DataBase.models import Persona
from Utils.utils import calcular_edad
import pandas as pd
from io import StringIO
from fastapi.responses import StreamingResponse

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

        # Crear DataFrame con formato tabular limpio
        df = pd.DataFrame(filas)
        
        buffer = StringIO()
        df.to_csv(buffer, index=False, sep=";", encoding="utf-8-sig")
        buffer.seek(0)
        
        return StreamingResponse(
            buffer,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=estado_personas_{habilitada}.csv"}
        )

    except Exception as e:
        print("Error en /csv/estado-personas:", str(e))
        raise HTTPException(status_code=500, detail="Error interno del servidor")