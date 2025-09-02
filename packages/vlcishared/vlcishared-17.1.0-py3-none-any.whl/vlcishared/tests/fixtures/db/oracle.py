from unittest.mock import MagicMock
import pytest


@pytest.fixture
def mock_oracle_patch(monkeypatch):
    """
    Fixture que mockea OracleConnector para evitar conexiones reales a Oracle.

    - Mockea los métodos execute_query, call_procedure y call_function.
    - Cada uno puede devolver una lista de mocks con atributo ._mapping (para simular filas).
    - Se puede simular error con side_effect.
    - Uso similar a mock_sqlserver_patch.

    Uso:
        def test_execute_query(mock_oracle_patch):
            mock_oracle = mock_oracle_patch(
                "modulo.OracleConnector",
                execute_query_return=[{"columna": "valor"}]
            )
            resultado = mock_oracle.execute_query()
            assert resultado[0]._mapping["columna"] == "valor"

        def test_call_function_error(mock_oracle_patch):
            mock_oracle = mock_oracle_patch(
                "modulo.OracleConnector",
                call_function_side_effect=Exception("Error en función")
            )
            with pytest.raises(Exception, match="Error en función"):
                mock_oracle.call_function("func_error")
    """

    def _patch(
        ruta_importacion: str,
        execute_query_return=None,
        execute_query_side_effect=None,
        execute_many_query_return=None,
        execute_many_query_side_effect=None,
        call_procedure_return=None,
        call_procedure_side_effect=None,
        call_function_return=None,
        call_function_side_effect=None,
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

        if execute_many_query_return is not None:
            rows = []
            for row_dict in execute_many_query_return:
                row_mock = MagicMock()
                row_mock._mapping = row_dict
                rows.append(row_mock)
            mock_connector_instance.execute_many_query.return_value = rows
        if execute_many_query_side_effect is not None:
            mock_connector_instance.execute_many_query.side_effect = execute_many_query_side_effect

        if call_procedure_return is not None:
            rows = []
            for row_dict in call_procedure_return:
                row_mock = MagicMock()
                row_mock._mapping = row_dict
                rows.append(row_mock)
            mock_connector_instance.call_procedure.return_value = rows
        if call_procedure_side_effect is not None:
            mock_connector_instance.call_procedure.side_effect = call_procedure_side_effect

        if call_function_return is not None:
            mock_connector_instance.call_function.return_value = call_function_return
        if call_function_side_effect is not None:
            mock_connector_instance.call_function.side_effect = call_function_side_effect

        mock_constructor = MagicMock(return_value=mock_connector_instance)
        monkeypatch.setattr(ruta_importacion, mock_constructor)

        return mock_connector_instance

    return _patch

