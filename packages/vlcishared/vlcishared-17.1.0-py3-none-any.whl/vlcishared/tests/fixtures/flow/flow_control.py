from unittest.mock import MagicMock

import pytest

from vlcishared.flow.flow import SUCCESS_EXEC, FlowControl


@pytest.fixture
def mock_flow_control_patch(monkeypatch):
    """
    Fixture que mockea la clase FlowControl para controlar su comportamiento durante los tests.

    - Reemplaza la clase FlowControl por un mock configurable.
    - Permite inyectar efectos colaterales personalizados en los métodos `handle_error` y `end_exec`.

    Parámetros:
    - ruta_importacion (str): Ruta completa donde se importa `FlowControl` (ej. "mi_paquete.mi_modulo.FlowControl").
    - handle_error_side_effect (callable|None): Lógica personalizada a ejecutar cuando se llama `handle_error`.
    - end_exec_side_effect (callable|None): Lógica personalizada a ejecutar cuando se llama `end_exec`.

    Uso:
        def test_algo(mock_flow_control_patch):
            mock_flow = mock_flow_control_patch("mi_modulo.FlowControl")
            ...
            mock_flow.handle_error.assert_called_once()
    """

    def _patch(
        ruta_importacion: str,
        handle_error_side_effect=None,
        end_exec_side_effect=None,
    ):
        mock_flow = MagicMock()

        if handle_error_side_effect is None:

            def real_handle_error(cause, fatal=False):
                return FlowControl.handle_error(mock_flow, cause, fatal)

            mock_flow.handle_error.side_effect = real_handle_error
        else:
            mock_flow.handle_error.side_effect = handle_error_side_effect

        if end_exec_side_effect is None:

            def real_end_exec():
                return FlowControl.end_exec(mock_flow)

            mock_flow.end_exec.side_effect = real_end_exec
        else:
            mock_flow.end_exec.side_effect = end_exec_side_effect

        mock_flow.flow_state = SUCCESS_EXEC

        monkeypatch.setattr(ruta_importacion, lambda *args, **kwargs: mock_flow)
        return mock_flow

    return _patch
