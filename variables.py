# ARCHIVO PARA GUARDAR LAS VARIABLES GLOBALES
from datetime import time

# ESTADO DE TURNOS
ESTADO_TURNO = ["Pendiente", "Cancelado", "Confirmado", "Asistido"]

# HORARIOS VÁLIDOS
HORARIOS_VALIDOS = [
    time(9,0), time(9,30), time(10,0), time(10,30), time(11,0), time(11,30),
    time(12,0), time(12,30), time(13,0), time(13,30), time(14,0), time(14,30),
    time(15,0), time(15,30), time(16,0), time(16,30)
    ]

MAX_CANCELADOS = 5