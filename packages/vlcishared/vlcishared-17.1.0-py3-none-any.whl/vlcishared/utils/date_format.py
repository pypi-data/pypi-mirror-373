import pandas as pd
import pytz


def obtener_inicial_dia_semana(serie_fechas: pd.Series) -> pd.Series:
    """
    Convierte una serie de fechas en formato string o datetime a una serie de letras
    que representan el día de la semana según la siguiente codificación:
    L = Lunes, M = Martes, X = Miércoles, J = Jueves, V = Viernes, S = Sábado, D = Domingo.

    Args:
        serie_fechas (pd.Series): Serie con fechas en formato string 'YYYY-MM-dd' o datetime.

    Returns:
        pd.Series: Serie con la letra del día de la semana correspondiente a cada fecha.
    """
    dias_semana = {0: "L", 1: "M", 2: "X", 3: "J", 4: "V", 5: "S", 6: "D"}
    return pd.to_datetime(serie_fechas).dt.weekday.map(dias_semana)


def convertir_fecha_a_tz(fecha, tz):
    """
    Transforma la fecha recibida a la fecha equivalente con el timezone recibido.
    - Si la fecha recibida es None, retorna None.
    - Si la fecha no tiene timezone, directamente se le aplica el timezone recibido.
    """
    if not fecha:
        return None

    if fecha.tzinfo is None:
        return tz.localize(fecha)
    else:
        return fecha.astimezone(tz)


def convertir_fecha_madrid_a_utc(fecha):
    """
    Convierte una fecha en formato ISO 8601 (string o datetime sin zona horaria)
    que representa una hora en la zona horaria de Madrid a su equivalente en UTC.

    Args:
        fecha (str or datetime-like): Fecha y hora en formato ISO 8601 sin zona horaria,
                                      que se asume está en hora local de Madrid.

    Returns:
        datetime: Objeto datetime con zona horaria UTC equivalente a la fecha de entrada.
    """
    zona_horaria_madrid = pytz.timezone("Europe/Madrid")
    fecha_hora_local = pd.to_datetime(fecha).tz_localize(zona_horaria_madrid)
    fecha_hora_utc = fecha_hora_local.astimezone(pytz.utc)
    return fecha_hora_utc
