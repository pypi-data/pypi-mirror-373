import os
from infisical_sdk import InfisicalSDKClient


INFISICAL_HOST = "https://eu.infisical.com"
PYTHON_ENV = os.getenv("PYTHON_ENV")
INFISICAL_CLIENT_ID = os.getenv("INFISICAL_CLIENT_ID")
INFISICAL_SECRET = os.getenv("INFISICAL_SECRET")
INFISICAL_PROJECT = os.getenv("INFISICAL_PROJECT")

class SecretNotFoundError(Exception):
    pass

class InfisicalClientSingleton:
    _instance = None
    _client = None
    _host = None
    _client_id = None
    _client_secret = None
    _project_id = None
    _python_env = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._initialize_client()
        return cls._instance

    @staticmethod
    def _initialize_client():
        InfisicalClientSingleton._host = INFISICAL_HOST
        InfisicalClientSingleton._client_id = INFISICAL_CLIENT_ID
        InfisicalClientSingleton._client_secret = INFISICAL_SECRET
        InfisicalClientSingleton._project_id = INFISICAL_PROJECT
        InfisicalClientSingleton._python_env = PYTHON_ENV

        client = InfisicalSDKClient(host=InfisicalClientSingleton._host)
        client.auth.universal_auth.login(
            client_id=InfisicalClientSingleton._client_id,
            client_secret=InfisicalClientSingleton._client_secret)

        InfisicalClientSingleton._client = client

    @classmethod
    def get_client(cls):
        return cls._client


def find_py_folder(current_path):
    """
    Busca una carpeta cuyo nombre empiece con 'py_' subiendo directorios hasta encontrarla.

    La búsqueda comienza desde el directorio especificado y sube hasta la raíz del sistema de archivos. 
    Si encuentra una carpeta cuyo nombre empieza con 'py_', retorna su nombre.

    Parámetros:
    -----------
    current_path : str
        Ruta desde donde se inicia la búsqueda.

    Retorna:
    --------
    str
        Ruta relativa que contiene el nombre de la carpeta que comienza con 'py_'.

    Excepciones:
    ------------
    FileNotFoundError
        Si no se encuentra ninguna carpeta cuyo nombre comience con 'py_' al subir por los directorios.
    """

    parent_dir = os.path.dirname(current_path)
    
    while parent_dir != current_path:
        folder_name = os.path.basename(current_path)

        if folder_name.startswith("py_"):
            return f"/{folder_name}"

        current_path = parent_dir
        parent_dir = os.path.dirname(current_path)
    raise FileNotFoundError("No se encontró una carpeta que comience con 'py_'.")

def get_secret(secret_name):
    """
    Obtiene el valor de un secreto desde Infisical.

    La función intenta obtener el secreto especificado desde la ruta adecuada:
    - Si el nombre del secreto comienza con 'GLOBAL_', se buscará en la carpeta raíz de Infisical.
    - Si no, se buscará en una carpeta de Infisical cuyo nombre será igual al de la ETL desde donde se ejecuta.

    Parámetros:
    -----------
    secret_name : str
        El nombre del secreto que se desea recuperar.

    Retorna:
    --------
    str
        El valor del secreto recuperado.

    Excepciones:
    ------------
    SecretNotFoundError
        Si no se encuentra el secreto, se lanza una excepción personalizada `SecretNotFoundError`.
    """
    if secret_name.startswith("GLOBAL_"):
        secret_path = "/"  
    else:
        execution_dir = os.getcwd()
        secret_path = find_py_folder(execution_dir)

    try:
        secret = InfisicalClientSingleton().get_client().secrets.get_secret_by_name(
            secret_name=secret_name,
            project_id=InfisicalClientSingleton._project_id,
            environment_slug=InfisicalClientSingleton._python_env,
            secret_path=secret_path
        )
    except Exception:
        raise SecretNotFoundError(f"El secreto '{secret_name}' no se encontró en '{secret_path}'.")

    return secret.secretValue
