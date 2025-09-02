import pytest

from vlcishared.tests.fixtures.db.postgresql import db_transaction, execute_query_side_effect_reemplazo_esquema, mock_postgres_patch  # noqa: F401


@pytest.fixture
def mock_postgres_gestion_fechas(mock_postgres_patch, db_transaction):  # noqa: F811
    mock = mock_postgres_patch(
        "gestion_fechas.repositorio.PostgresConnector.instance", execute_query_side_effect=execute_query_side_effect_reemplazo_esquema(db_transaction)
    )
    return mock
