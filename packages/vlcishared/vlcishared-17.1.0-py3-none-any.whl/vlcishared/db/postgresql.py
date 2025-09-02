from sqlalchemy import text
import logging
from typing import Any, List, Sequence, Tuple
import pandas as pd
from sqlalchemy import Row, TextClause, create_engine
from sqlalchemy.orm import sessionmaker
from vlcishared.utils.interfaces import ConnectionInterface
from sqlalchemy.engine import Connection


class PostgresConnector(ConnectionInterface):
    _instance = None

    @classmethod
    def instance(cls):
        if not cls._instance:
            raise Exception("PostgresConnector no ha sido inicializado aún.")
        return cls._instance

    def __new__(cls, host, port, database, user, password):
        if cls._instance is None:
            cls._instance = super(PostgresConnector, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, host: str, port: str, database: str, user: str, password: str):
        if self._initialized:
            return  # Ya fue inicializado, evitar reiniciar
        self.log = logging.getLogger()
        self.db_name = database
        self.connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        self.connect()
        self._initialized = True

    def connect(self):
        """Función que se conecta a la base de datos definida en el constructor"""
        self.engine = create_engine(self.connection_string)
        self.session_maker = sessionmaker(bind=self.engine)
        self.session = self.session_maker()
        self.log.info(f"Conectado a {self.db_name}")

    def close(self):
        """Cierra la conexión con la base de datos"""
        if self.session:
            self.session.close()
        if self.engine:
            self.engine.dispose()
        self.log.info(f"Desconectado de {self.db_name}.")

    def call_procedure(self, procedure_name: str, *params: Any):
        """
        Llama a un procedimiento almacenado en la base de datos.

        Args:
            procedure_name (str): Nombre del procedimiento almacenado.
            *params (Any): Parámetros posicionales que se pasan al procedimiento.
                Se asignan automáticamente a placeholders (:p0, :p1, ...).

        Raises:
            Exception: Si la ejecución del procedimiento falla.
        """
        try:
            param_placeholders, param_dict = self._create_placeholder_params(params)
            sql = text(f"CALL {procedure_name}({param_placeholders})")
            self.session.execute(sql, param_dict)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            self.log.error(f"Fallo llamando al procedimiento {procedure_name}: {e}")
            raise e

    def call_function(self, function_name: str, *params: Any) -> Sequence[Row[Any]]:
        """
        Llama a una función almacenada en la base de datos y devuelve su resultado.

        Args:
            function_name (str): Nombre de la función almacenada.
            *params (Any): Parámetros posicionales que se pasan al procedimiento.
                Se asignan automáticamente a placeholders (:p0, :p1, ...).

        Returns:
            Sequence[Row[Any]]: Lista de filas devueltas por la función.
                - Si la función retorna un escalar: se obtiene un único Row con una sola columna.
                - Si la función retorna un setof: se obtiene una lista de Row con múltiples registros.

        Raises:
            Exception: Si la ejecución de la función falla.
        """
        try:
            param_placeholders, param_dict = self._create_placeholder_params(params)
            sql = text(f"SELECT {function_name}({param_placeholders})")
            result = self.session.execute(sql, param_dict)
            self.session.commit()
            return result.fetchall()
        except Exception as e:
            self.session.rollback()
            self.log.error(f"Fallo llamando a la función {function_name}: {e}")
            raise e

    def _create_placeholder_params(self, params: List[Any]):
        placeholders = ", ".join([f":p{i}" for i in range(len(params))])
        param_dict = {f"p{i}": param for i, param in enumerate(params)}
        return placeholders, param_dict

    def execute_query(self, query: str | TextClause, params: dict = None, commit: bool = True, conn: Connection = None):
        """
        Ejecuta una consulta SQL, con o sin commit.

        Args:
            query (str | TextClause): Consulta SQL a ejecutar.
            params (dict, optional): Parámetros para la query.
            commit (bool, optional):
                - Si True: se abre una transacción con `engine.begin()` y se hace commit automáticamente al salir del contexto.
                - Si False: se abre una conexión simple con `engine.connect()` (sin transacción implícita, sin commit). Útil para SELECTs.
            conn (Connection, optional):
                Conexión ya existente a reutilizar. En este caso, no se abre ni se cierra nada dentro de esta función
                y el control de commit/rollback queda fuera.

        Returns:
            Result: El resultado de la ejecución de la query.

        Raises:
            Exception: Si la ejecución de la consulta falla.
        """
        try:
            query_obj = text(query) if isinstance(query, str) else query
            if conn:
                return conn.execute(query_obj, params or {})
            else:
                execution_context = self.engine.begin() if commit else self.engine.connect()
                with execution_context as conn:
                    result = conn.execute(query_obj, params or {})
                return result
        except Exception as e:
            self.log.error(f"Error al ejecutar la consulta: {e}")
            raise

    def execute_multiple_queries(self, queries_with_params: List[Tuple[str, dict]], conn: Connection = None):
        """
        Ejecuta múltiples consultas SQL distintas dentro de una única transacción. Si alguna falla, se hace rollback automático.
        Cada consulta es ejecutada una vez con su conjunto específico de parámetros.

        Args:
            queries_with_params (List[Tuple[str, dict]]):
                Lista de tuplas donde cada tupla contiene:
                - query (str): Consulta SQL parametrizada.
                - params (dict): Diccionario con valores para los parámetros de la consulta.
            conn (Connection, optional):
                Conexión ya existente a reutilizar. En este caso, no se abre ni se cierra nada dentro de esta función
                y el control de commit/rollback queda fuera.

        Raises:
            Exception: Si la ejecución de la consulta falla.
        """
        try:
            if conn:
                for query, params in queries_with_params:
                    conn.execute(text(query), params)
            else:
                with self.engine.begin() as trans:
                    for query, params in queries_with_params:
                        trans.execute(text(query), params)
            self.log.info("Todas las queries se ejecutaron correctamente.")
        except Exception as e:
            self.log.error(f"Error al ejecutar las queries: {e}")
            raise

    def insert_many_rows(self, query: str | TextClause, df: pd.DataFrame, conn: Connection = None):
        """
        Ejecuta una única consulta parametrizada en batch para insertar múltiples filas.
        La consulta SQL debe estar preparada para recibir múltiples sets de parámetros (una fila por set),
        típicamente un INSERT con placeholders nombrados.

        Args:
            query (str): Consulta SQL parametrizada.
                Debe usar placeholders con nombre, por ejemplo: "INSERT INTO tabla (col1, col2) VALUES (:col1, :col2)"
            df (pd.DataFrame): DataFrame que contiene los datos a insertar.
                Cada fila se convertirá en un diccionario de parámetros para la consulta SQL.
            conn (Connection, optional):
                Conexión ya existente a reutilizar. En este caso, no se abre ni se cierra nada dentro de esta función
                y el control de commit/rollback queda fuera.

        Raises:
            Exception: Si la ejecución de la consulta falla.

        """
        try:
            if df.empty:
                self.log.info("DataFrame vacío, no se inserta nada")
                return

            query_obj = text(query) if isinstance(query, str) else query
            params_list = df.to_dict(orient="records")

            if conn:
                conn.execute(query_obj, params_list)
            else:
                with self.engine.begin() as trans:
                    trans.execute(query_obj, params_list)
            self.log.info(f"Ejecutadas {len(df)} filas con la consulta parametrizada.")
        except Exception as e:
            self.log.error(f"Error al insertar múltiples registros: {e}")
            raise
