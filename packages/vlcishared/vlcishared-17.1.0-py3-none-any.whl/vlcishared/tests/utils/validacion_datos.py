import math
from datetime import datetime
from decimal import Decimal

from vlcishared.utils.date_format import convertir_fecha_a_tz


def convertir_campos_fechas_a_tz(rows, tz, campos=("fen", "fen_inicio", "fen_fin")):
    resultado_convertido = []

    for row in rows:
        nuevo_row = dict(row)
        for campo in campos:
            if campo in nuevo_row:
                nuevo_row[campo] = convertir_fecha_a_tz(row[campo], tz)
        resultado_convertido.append(nuevo_row)

    return resultado_convertido


def comparar_filas_con_esperadas(filas, esperados):
    assert len(filas) == len(esperados)
    for fila, esperado in zip(filas, esperados):
        for key in esperado:
            if isinstance(esperado[key], datetime) and isinstance(fila[key], datetime):
                diff = abs((esperado[key].replace(tzinfo=None) - fila[key].replace(tzinfo=None)).total_seconds())
                assert diff < 60, f"Error en campo fecha {key} (tolerancia 1m): esperado {esperado[key]}, obtenido {fila[key]}"
            elif isinstance(esperado[key], Decimal) and isinstance(fila[key], float):
                valor_dec = Decimal(str(fila[key]))
                assert esperado[key] == valor_dec, f"Error en campo {key}: esperado {esperado[key]}, obtenido {valor_dec}"
            elif isinstance(esperado[key], float) and isinstance(fila[key], Decimal):
                valor_dec = Decimal(str(esperado[key]))
                assert fila[key] == valor_dec, f"Error en campo {key}: esperado {valor_dec}, obtenido {fila[key]}"
            elif isinstance(esperado[key], float) and isinstance(fila[key], float):
                assert math.isclose(esperado[key], fila[key], rel_tol=1e-9), f"Error en valor: esperado {esperado[key]}, obtenido {fila[key]}"
            else:
                assert esperado[key] == fila[key], f"Error en campo {key}: esperado {esperado[key]}, obtenido {fila[key]}"
