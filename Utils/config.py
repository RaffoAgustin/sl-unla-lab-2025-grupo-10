import os
from dotenv import load_dotenv
from datetime import time
from enum import Enum
import json
from dotenv import load_dotenv
from decimal import Decimal

# Esta línea lee el archivo .env y carga sus variables en el entorno
load_dotenv("Utils/variables.env")

# Leemos la variable DATABASE_URL del entorno.
DATABASE_URL = os.getenv("DATABASE_URL")

# Leer la variable ESTADOS_TURNO
estados_strings = os.getenv("ESTADOS_TURNO", "") #Obtiene la variable de ESTADOS_TURNO como un string, o vacio si no lo obtiene
values = [v for v in estados_strings.split(",") if v] #Divido el string en comas ["Pendiente", "Cancelado", ...]

if not values: #Validación por seguridad
    raise ValueError("La variable ESTADOS_TURNO está vacía o mal definida")

ESTADOS_TURNO = Enum("ESTADOS_TURNO",  # Nombre interno del Enum
                    {v: v for v in values}, # Diccionario {clave: valor}, el valor es igual a la clave en este caso
                    type=str)  # Hace que cada miembro sea un str real

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
            print(
                f"ERROR: El formato de hora '{horario_str}' en .env es inválido y será ignorado.")


# Leer la variable MESES
meses_str = os.getenv("MESES")
# Se crea la lista, si no hay, por seguridad se crea vacia
MESES = meses_str.split(',') if meses_str else []

# Leer la variable MAX_CANCELADOS
max_cancelados_str = os.getenv("MAX_CANCELADOS")
MAX_CANCELADOS = int(max_cancelados_str) if max_cancelados_str else 5

# Leer la variable CANT_ELEMENTOS_X_PAGINA
cant_elementos_x_pagina_str = os.getenv("CANT_ELEMENTOS_X_PAGINA")
CANT_ELEMENTOS_X_PAGINA = int(cant_elementos_x_pagina_str) if cant_elementos_x_pagina_str else 5

#Leer variables de configuración de PDF

def formatear_pdf_config(nombre_config_env: str):
    raw = os.getenv(nombre_config_env) #Busca la variable de entorno con el nombre indicado
    if not raw: #Si no encuentra, lanza excepción
        raise ValueError(f"Variable de entorno {nombre_config_env} no encontrada")

    config = json.loads(raw) #Convierte la variable de entorno a formato json

    # Convertir campos necesarios a Decimal
    config["page_width"] = Decimal(config["page_width"])
    config["page_height"] = Decimal(config["page_height"])
    config["column_widths"] = [Decimal(x) for x in config["column_widths"]]
    config["max_rows"] = int(config["max_rows"])

    return config

# Creamos accesores simples:
CONFIG_PDF_PERSONA = formatear_pdf_config("CONFIG_PDF_PERSONA")
CONFIG_PDF_TURNOS = formatear_pdf_config("CONFIG_PDF_TURNOS")