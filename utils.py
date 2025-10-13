from datetime import datetime, date, time
from dateutil.relativedelta import relativedelta

def calcular_edad(fecha):
    for f in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try: 
            fecha = datetime.strptime(fecha, f).date()
            break
        except:
            pass
    else:
        raise ValueError("Formato no válido.")
    return relativedelta(date.today(), fecha).years

HORARIOS_VALIDOS = [
    time(9,0), time(9,30), time(10,0), time(10,30), time(11,0), time(11,30),
    time(12,0), time(12,30), time(13,0), time(13,30), time(14,0), time(14,30),
    time(15,0), time(15,30), time(16,0), time(16,30), time(17,0)
    ]

def es_horario_valido(hora):
    return hora in HORARIOS_VALIDOS