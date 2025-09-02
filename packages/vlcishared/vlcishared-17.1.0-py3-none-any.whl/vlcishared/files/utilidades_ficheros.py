from datetime import datetime
import re

def ordenar_ficheros_por_fecha_en_nombre(formato_fecha, ficheros):
    """
    Ordena una lista de nombres de ficheros según la fecha contenida en su nombre.

    Args:
        formato_fecha (str): Formato en el que está escrita la fecha en el nombre del fichero (por ejemplo: '%Y%m%d', '%Y_%m_%d').
        ficheros (list of str): Lista de nombres de ficheros a ordenar.

    Returns:
        list of str: Lista de nombres de ficheros ordenados cronológicamente según la fecha extraída.
    """
    archivos_con_fecha = []
    for fichero in ficheros:
        fecha = extraer_fecha_desde_nombre_fichero(formato_fecha, fichero)
        archivos_con_fecha.append((fecha, fichero))

    archivos_con_fecha.sort(key=lambda x: x[0])
    return [nombre for _, nombre in archivos_con_fecha]

def extraer_fecha_desde_nombre_fichero(formato_fecha, nombre_fichero):
    """
    Extrae la fecha del nombre de un fichero usando un patrón regex y un formato específico.

    Args:
        formato_fecha (str): Formato en el que está escrita la fecha en el nombre del fichero (por ejemplo: '%Y%m%d', '%Y_%m_%d').
        nombre_fichero (str): Nombre del fichero del que extraer la fecha.

    Returns:
        datetime: Objeto datetime con la fecha extraída.

    Raises:
        ValueError: Si no se encuentra una fecha válida en el nombre del fichero o el formato no coincide.
    """
    patron_fecha_str = formato_a_patron_regex(formato_fecha)
    patron_fecha_compilado = re.compile(patron_fecha_str)
    match = patron_fecha_compilado.search(nombre_fichero)
    if not match:
        raise ValueError(f"El fichero {nombre_fichero} no contiene una fecha válida")

    fecha_str = match.group(0)
    return datetime.strptime(fecha_str, formato_fecha)

def formato_a_patron_regex(formato_fecha: str) -> str:
    r"""
    Convierte un formato de fecha de datetime a un patrón regex.
    
    Args:
        formato_fecha (str): como '%Y_%m_%d' o '%d-%m-%Y'
    
    Returns:
        str: patrón regex equivalente, ej: r"\d{4}_\d{2}_\d{2}"
    """
    mapping = {
        "%Y": r"\d{4}",
        "%y": r"\d{2}",
        "%m": r"\d{2}",
        "%d": r"\d{2}",
    }

    patron = formato_fecha
    for token, regex_equivalente in mapping.items():
        patron = patron.replace(token, regex_equivalente)

    patron = re.sub(r"(?<!\\)([^\w\\{}])", r"\\\1", patron)
    return patron

