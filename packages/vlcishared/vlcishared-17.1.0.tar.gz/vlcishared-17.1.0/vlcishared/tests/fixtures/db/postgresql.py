from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine, text

from vlcishared.env_variables.secrets import get_secret
from vlcishared.tests.fixtures.db.schema_utils import borrar_funciones_y_procedimientos, borrar_tablas, copiar_funciones_y_procedimientos, copiar_tablas

from contextlib import contextmanager


@pytest.fixture
def mock_postgres_patch(monkeypatch, db_transaction):
    """
    Fixture que mockea PostgresConnector para ejecutar queries sobre una base de datos real (SQLite/PostgreSQL de prueba).

    - Redirige métodos como connect, execute y execute_query al engine de pruebas.
    - Permite testear sin conectarse a una base de datos real de producción.
    - Requiere la ruta del import de PostgresConnector.

    Parámetros:
    - ruta_importacion (str): Ruta completa donde se importa `PostgresConnector` (ej. "mi_paquete.mi_modulo.PostgresConnector").
    - call_procedure_side_effect (callable|None): Lógica personalizada a ejecutar cuando se llama `call_procedure`.
    - call_function_side_effect (callable|None): Lógica personalizada a ejecutar cuando se llama `call_function`.
    - execute_query_side_effect (callable|None): Lógica personalizada a ejecutar cuando se llama `execute_query`.
    - execute_multiple_queries_side_effect (callable|None): Lógica personalizada a ejecutar cuando se llama `execute_multiple_queries`.
    - insert_many_rows_side_effect (callable|None): Lógica personalizada a ejecutar cuando se llama `insert_many_rows`.

    Uso:
        def test_xxx(mock_db_patch):
            mock_db = mock_db_patch("modulo.donde.importa.PostgresConnector")
            mock_db.execute.assert_called_once()
    """

    def _patch(
        target_path: str,
        call_procedure_side_effect=None,
        call_function_side_effect=None,
        execute_query_side_effect=None,
        execute_multiple_queries_side_effect=None,
        insert_many_rows_side_effect=None,
    ):
        mock_connector = MagicMock()

        mock_connector.connect.return_value = db_transaction
        mock_connector.close.return_value = None

        mock_connector.call_procedure.side_effect = call_procedure_side_effect or call_procedure_side_effect_default(db_transaction)
        mock_connector.call_function.side_effect = call_function_side_effect or call_function_side_effect_default(db_transaction)
        mock_connector.execute_query.side_effect = execute_query_side_effect or execute_query_side_effect_default(db_transaction)
        mock_connector.execute_multiple_queries.side_effect = execute_multiple_queries_side_effect or execute_multiple_queries_side_effect_default(
            db_transaction
        )
        mock_connector.insert_many_rows.side_effect = insert_many_rows_side_effect or insert_many_rows_side_effect_default(db_transaction)
        mock_connector.engine = db_transaction

        mock_connector.engine = db_transaction

        # @contextmanager te envuelve esa función en un objeto que implementa __enter__ y __exit__
        # sirve para cuando en la ETL hacemos with PostgresConnector.instance().engine.begin as conn:
        @contextmanager
        def fake_begin():
            trans = db_transaction.begin_nested()
            try:
                yield db_transaction  # esto es lo que se asigna a `conn` dentro del with (__enter__)
                trans.commit()  # esto actua como el __exit__
            except Exception:
                trans.rollback()  # esto actua como el __exit__
                raise

        mock_connector.engine.begin = fake_begin

        monkeypatch.setattr(target_path, lambda *args, **kwargs: mock_connector)
        return mock_connector

    yield _patch


@pytest.fixture
def db_transaction(connection):
    transaction = connection.begin_nested()
    yield connection
    transaction.rollback()


@pytest.fixture(scope="session")
def connection():
    """
    Crea una conexión de SQLAlchemy contra una base de datos PostgreSQL de prueba.

    - Devuelve una conexión viva que se cierra al finalizar el test.
    - Usado por otros fixtures para ejecutar queries reales en un entorno aislado.
    """
    user = get_secret("GLOBAL_DATABASE_POSTGIS_LOGIN_TEST")
    password = get_secret("GLOBAL_DATABASE_POSTGIS_PASSWORD_TEST")
    port = get_secret("GLOBAL_DATABASE_POSTGIS_PORT_TEST")
    host = get_secret("GLOBAL_DATABASE_POSTGIS_HOST_TEST")
    database = get_secret("GLOBAL_DATABASE_POSTGIS_DATABASE_TEST")
    schema = get_secret("GLOBAL_DATABASE_POSTGIS_SCHEMA_TEST")
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    engine = create_engine(url)
    connection = engine.connect()
    connection.execute(text(f"SET search_path TO {schema}"))
    yield connection
    connection.close()
    engine.dispose()


@pytest.fixture(scope="session", autouse=True)
def setup_esquema_test_desde_vlci2(connection):
    """
    Fixture que se ejecuta una vez por sesión de pytest (scope="session") y automáticamente en todas las pruebas (autouse=True).

    - Copia las tablas y funciones/procedimientos del esquema 'vlci2' al esquema de test.
    - Al finalizar la sesión, elimina las tablas y funciones/procedimientos del esquema de test.

    Si se necesita preparar el esquema de test a partir de un origen distinto, se puede definir un nuevo fixture personalizado en el módulo correspondiente:
    @pytest.fixture(scope="session", autouse=True)
        def setup_esquema_xxx_desde_yyy(connection):
            copiar_esquema(connection, esquema_yyy, esquema_xxx)
            yield
            limpiar_esquema(connection, esquema_xxx)
    """
    esquema_vlci2 = get_secret("GLOBAL_DATABASE_POSTGIS_SCHEMA_VLCI2")
    esquema_test = get_secret("GLOBAL_DATABASE_POSTGIS_SCHEMA_TEST")
    copiar_esquema(connection, esquema_vlci2, esquema_test)
    yield
    limpiar_esquema(connection, esquema_test)


def copiar_esquema(connection, esquema_origen, esquema_destino):
    """
    Copia tablas y funciones/procedimientos del esquema origen al destino usando la misma conexión.
    """
    copiar_tablas(connection, esquema_origen, esquema_destino)
    copiar_funciones_y_procedimientos(connection, esquema_origen, esquema_destino)


def limpiar_esquema(connection, esquema):
    """
    Borra tablas y funciones/procedimientos del esquema indicado usando la misma conexión.
    """
    borrar_tablas(connection, esquema)
    borrar_funciones_y_procedimientos(connection, esquema)


def call_procedure_side_effect_default(transaction):
    def _call_procedure(procedure_name, *params):
        placeholders = ", ".join([f":p{i}" for i in range(len(params))])
        param_dict = {f"p{i}": param for i, param in enumerate(params)}
        sql = text(f"CALL {procedure_name}({placeholders})")
        transaction.execute(sql, param_dict)

    return with_rollback(transaction, _call_procedure)


def call_function_side_effect_default(transaction):
    def _call_procedure(procedure_name, *params):
        placeholders = ", ".join([f":p{i}" for i in range(len(params))])
        param_dict = {f"p{i}": param for i, param in enumerate(params)}
        result = transaction.execute(text(f"SELECT {procedure_name}({placeholders})"), param_dict)
        return result.fetchall()

    return with_rollback(transaction, _call_procedure)


def execute_query_side_effect_default(transaction):

    def _execute_query(query, params=None, commit=True, conn=None):
        query_obj = text(query) if isinstance(query, str) else query
        if conn:
            return conn.execute(query_obj, params or {})
        else:
            if commit:
                return transaction.execute(query_obj, params or {})
            else:
                # Savepoint para aislar la query
                trans = transaction.begin_nested()
                try:
                    result = transaction.execute(query_obj, params or {})
                finally:
                    trans.rollback()  # revierte solo esta query
                return result

    return with_rollback(transaction, _execute_query)


def execute_multiple_queries_side_effect_default(transaction):

    def _execute_multiple_queries(queries_with_params, conn=None):
        if conn:
            for query, params in queries_with_params:
                conn.execute(text(query), params)
        else:
            trans = transaction.begin_nested()
            try:
                for query, params in queries_with_params:
                    transaction.execute(text(query), params)
            except Exception:
                trans.rollback()

    return with_rollback(transaction, _execute_multiple_queries)


def insert_many_rows_side_effect_default(transaction):

    def _insert_query_commit(query, df, conn=None):
        if df.empty:
            return

        query_obj = text(query) if isinstance(query, str) else query
        params_list = df.to_dict(orient="records")
        if conn:
            conn.execute(query_obj, params_list)
        else:
            transaction.execute(query_obj, params_list)

    return with_rollback(transaction, _insert_query_commit)


def with_rollback(transaction, func):
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            transaction.rollback()
            raise

    return wrapped


def execute_query_side_effect_reemplazo_esquema(transaction, esquema_original="vlci2", esquema_reemplazo="test_component"):  # noqa: F811
    def _execute(query, params=None, commit=True, conn=None):
        query_modificada = _reemplazar_query(query, esquema_original, esquema_reemplazo)
        funcion = execute_query_side_effect_default(transaction)
        return funcion(query_modificada, params, commit, conn)

    return _execute


def execute_multiple_queries_side_effect_reemplazo_esquema(transaction, esquema_original="vlci2", esquema_reemplazo="test_component"):  # noqa: F811
    def _execute(queries_with_params, conn=None):
        querys_modificadas = [(_reemplazar_query(query, esquema_original, esquema_reemplazo), params) for query, params in queries_with_params]
        funcion = execute_multiple_queries_side_effect_default(transaction)
        return funcion(querys_modificadas, conn)

    return _execute


def insert_many_rows_side_effect_reemplazo_esquema(transaction, esquema_original="vlci2", esquema_reemplazo="test_component"):  # noqa: F811
    def _execute(query, df, conn=None):
        query_modificada = _reemplazar_query(query, esquema_original, esquema_reemplazo)
        funcion = insert_many_rows_side_effect_default(transaction)
        return funcion(query_modificada, df, conn)

    return _execute


def _reemplazar_query(query, esquema_original, esquema_reemplazo):
    query_str = query if isinstance(query, str) else str(query)
    return query_str.replace(esquema_original, esquema_reemplazo)
