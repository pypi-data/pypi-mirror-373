from unittest.mock import MagicMock
import pytest

@pytest.fixture
def mock_sqlserver_patch(monkeypatch):
    """
    Fixture que mockea SqlServerConnector para evitar conexiones reales a SQL Server.

    - Mockea el método execute_query devolviendo una lista de mocks con atributo ._mapping
      para simular resultados de SQLAlchemy.
    - Permite testear funciones que acceden a los resultados usando ._mapping.
    - Permite simular errores con side_effect si se necesita.

    Uso:
        def test_xxx(mock_sqlserver_patch):
            mock_sqlserver = mock_sqlserver_patch(
                "modulo.SqlServerConnector",
                execute_query_return=[{"columna": "valor"}]
            )
            resultado = mock_sqlserver.execute_query()
            assert resultado[0]._mapping["columna"] == "valor"

        def test_yyy(mock_sqlserver_patch):
            mock_sqlserver = mock_sqlserver_patch(
                "modulo.SqlServerConnector",
                execute_query_side_effect=Exception("Error simulado")
            )
            with pytest.raises(Exception, match="Error simulado"):
                mock_sqlserver.execute_query()
    """

    def _patch(
        ruta_importacion: str,
        execute_query_return=None,
        execute_query_side_effect=None
    ):
        mock_connector_instance = MagicMock()

        if execute_query_return is not None:
            rows = []
            for row_dict in execute_query_return:
                row_mock = MagicMock()
                row_mock._mapping = row_dict
                rows.append(row_mock)
            mock_connector_instance.execute_query.return_value = rows

        if execute_query_side_effect is not None:
            mock_connector_instance.execute_query.side_effect = execute_query_side_effect

        mock_constructor = MagicMock(return_value=mock_connector_instance)
        monkeypatch.setattr(ruta_importacion, mock_constructor)

        return mock_connector_instance

    return _patch
