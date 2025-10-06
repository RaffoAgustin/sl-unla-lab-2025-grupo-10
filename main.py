# main.py
#Importaciones de FastAPI y los routers de los distintos archivos
from fastapi import FastAPI
from DataBase.database import Base, engine
from Personas.alta_persona import router as personas_router
from Personas.listado_personas import router as listado_persona_router
from Personas.obtener_persona import router as persona_router
from Personas.eliminar_persona import router as eliminar_router
from Personas.modificar_persona import router as modificar_router
from Turnos.alta_turno import router as turnos_router
from Turnos.eliminar_turno import router as eliminar_turno_router
from Turnos.modificar_turno import router as modificar_turno
from Turnos.listado_turnos import router as listado_turnos
from Turnos.obtener_turno_particular import router as obtener_turno_particular
from Turnos.calculo_turnos_disponibles import router as calculo_turnos_disponibles
from Turnos.turnos_de_una_fecha import router as turnos_de_una_fecha
from Turnos.turnos_de_una_persona import router as turnos_de_una_persona

app = FastAPI(title="Mi API")

Base.metadata.create_all(bind=engine)

app.include_router(personas_router, prefix="/personas", tags=["Personas"])
app.include_router(listado_persona_router, prefix="/listado_personas", tags=["Listado completo de Personas"])
app.include_router(persona_router, prefix="/obtener_persona", tags=["Listado de una Persona especifica"])
app.include_router(eliminar_router, prefix="/eliminar_persona", tags=["Eliminar Persona"])
app.include_router(modificar_router, prefix="/modificar_persona", tags=["Modificar Persona"])

app.include_router(turnos_router, tags=["Turnos"])
app.include_router(eliminar_turno_router, prefix="/eliminar_turno", tags=["Eliminar Turno"])
app.include_router(modificar_turno, prefix="/modificar_turno", tags=["Modificar Turno"])
app.include_router(listado_turnos, prefix="/listado_turnos", tags=["Listado Turnos"])
app.include_router(obtener_turno_particular, prefix="/obtener_turno_particular", tags=["Obtener Turno Particular"])
app.include_router(calculo_turnos_disponibles,prefix="/calculo_turnos_disponibles", tags=["Calcular Turnos Disponibles"])
app.include_router(turnos_de_una_fecha,prefix="/turnos_de_una_fecha", tags=["Obtener Turnos De Una Fecha"])
app.include_router(turnos_de_una_persona,prefix="/turnos_de_una_persona", tags=["Obtener Turnos De Una Persona"])

@app.get("/")
def read_root():
    return {"mensaje": "¡Proyecto base funcionando!"}
