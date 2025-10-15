import os
from dotenv import load_dotenv
from datetime import time

# Esta línea lee el archivo .env y carga sus variables en el entorno
load_dotenv("Utils/variables.env")

# Leemos la variable DATABASE_URL del entorno.
DATABASE_URL = os.getenv("DATABASE_URL")

# Leer la variable ESTADOS_TURNO
estados_strings = os.getenv("ESTADOS_TURNO")
ESTADOS_TURNO = estados_strings.split(',') if estados_strings else [] #Se crea la lista, si no hay, por seguridad se crea vacia

# Inicializar lista de horarios válidos
HORARIOS_VALIDOS = []

# Leer la variable de HORARIOS_VALIDOS
horarios_str = os.getenv("HORARIOS_VALIDOS")

if horarios_str:
    # Separamos el string por comas para obtener cada "HH:MM"
    for horario_str in horarios_str.split(','):
        # Usamos strptime para convertir el string a un objeto time
        try:
            horario_obj = time.fromisoformat(horario_str.strip())
            HORARIOS_VALIDOS.append(horario_obj)
        except ValueError:
            print(f"ERROR: El formato de hora '{horario_str}' en .env es inválido y será ignorado.")

# Leer la variable MAX_CANCELADOS
max_cancelados_str = os.getenv("MAX_CANCELADOS")
MAX_CANCELADOS = int(max_cancelados_str) if max_cancelados_str else 5