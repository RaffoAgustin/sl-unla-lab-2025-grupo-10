from dateutil.relativedelta import relativedelta
from datetime import datetime, date
from variables import HORARIOS_VALIDOS

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

def es_horario_valido(hora):
    return hora in HORARIOS_VALIDOS