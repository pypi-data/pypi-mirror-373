import logging
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from vlcishared.utils.interfaces import ConnectionInterface


class SQLServerConnector(ConnectionInterface):
    """
    Clase para gestionar la conexión a una base de datos SQL Server mediante SQLAlchemy.
    Implementa el patrón Singleton para asegurar que solo haya una instancia activa.
    """

    _instance = None 

    @classmethod
    def instance(cls):
        """
        Devuelve la instancia única de SQLServerConnector, si ha sido inicializada.
        Lanza una excepción si se intenta acceder antes de inicializarla.
        """
        if not cls._instance:
            raise Exception("SQLServerConnector no ha sido inicializado aún.")
        return cls._instance

    def __new__(cls, *args, **kwargs):
        """
        Crea una nueva instancia si no existe una ya creada (patrón Singleton).
        """
        if cls._instance is None:
            cls._instance = super(SQLServerConnector, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(
        self,
        host: str,
        port: str,
        database: str,
        user: str,
        password: str,
        driver: str = "ODBC Driver 18 for SQL Server"
    ):
        """
        Inicializa la conexión a la base de datos SQL Server si no ha sido ya inicializada.
        Crea el string de conexión y establece la conexión usando SQLAlchemy.
        """
        if self._initialized:
            return 

        self.log = logging.getLogger()
        self.connection_string = (
            f"mssql+pyodbc://{user}:{password}@{host},{port}/{database}"
            f"?driver={driver.replace(' ', '+')}&TrustServerCertificate=yes"
        )

        self.connect()
        self._initialized = True

    def connect(self):
        """
        Establece la conexión a la base de datos utilizando SQLAlchemy.
        Crea un engine y una sesión para ejecutar queries posteriormente.
        """
        self.engine = create_engine(self.connection_string)
        self.session_maker = sessionmaker(bind=self.engine)
        self.session = self.session_maker()
        self.log.info(f"Conectado a SQL Server")

    def close(self):
        """
        Cierra la sesión y libera los recursos del engine.
        """
        if self.session:
            self.session.close()
        if self.engine:
            self.engine.dispose()
        self.log.info(f"Desconectado de SQL Server")

    def execute_query(self, query: str, params: dict = None) -> Any:
        """
        Ejecuta una consulta SQL utilizando la sesión activa.
        
        :param query: Consulta SQL a ejecutar.
        :param params: Parámetros opcionales para la consulta.
        :return: Objeto de resultados de SQLAlchemy.
        :raises: Re-lanza cualquier excepción ocurrida durante la ejecución.
        """
        try:
            result = self.session.execute(text(query), params or {})
            return result
        except Exception as e:
            self.log.error(f"Error al ejecutar la query: {e}")
            raise
