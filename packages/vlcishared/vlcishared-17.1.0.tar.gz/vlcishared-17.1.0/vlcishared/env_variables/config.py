import os
import configparser

class ConfigNotFoundError(Exception):
    """Se lanza cuando una variable no se encuentra en el archivo de configuración."""
    pass

NOMBRE_FICHERO = "config.ini"

def find_config(current_path):
    """
    Busca `config.ini` subiendo directorios hasta encontrarlo.

    Parámetros:
    -----------
    current_path : str
        Ruta desde donde se inicia la búsqueda.

    Retorna:
    --------
    str
        Ruta absoluta del archivo `config.ini`.

    Excepciones:
    ------------
    FileNotFoundError
        Si no se encuentra el archivo tras recorrer todos los niveles.
    """
    parent_path = os.path.dirname(current_path)

    while parent_path != current_path:
        config_path = os.path.join(current_path, NOMBRE_FICHERO)

        if os.path.exists(config_path):
            return config_path

        current_path = parent_path
        parent_path = os.path.dirname(current_path)

    raise FileNotFoundError(f"No se encontró el fichero '{NOMBRE_FICHERO}' en ninguno de los directorios.")

def read_config():
    """Lee el archivo `config.ini`, buscando desde donde se ejecutó el script."""
    execution_dir = os.getcwd() 
    config_path = find_config(execution_dir)

    config = configparser.ConfigParser()
    config.read(config_path)
    return config

def get_config(variable_name):
    """
    Obtiene el valor de una variable desde el archivo de configuración `config.ini`.

    La función busca la variable en todas las secciones del archivo de configuración.

    Parámetros:
    -----------
    variable_name : str
        El nombre de la variable a recuperar.

    Retorna:
    --------
    str
        El valor de la variable encontrada en el archivo de configuración.

    Excepciones:
    ------------
    ConfigNotFoundError
        Si no se encuentra la variable en ninguna de las secciones del archivo.
    """
    config = read_config()

    for section in config.sections():
        if variable_name in config[section]:
            return config[section][variable_name]
    
    raise ConfigNotFoundError(f"Error al obtener la variable '{variable_name}' del fichero '{NOMBRE_FICHERO}'.")