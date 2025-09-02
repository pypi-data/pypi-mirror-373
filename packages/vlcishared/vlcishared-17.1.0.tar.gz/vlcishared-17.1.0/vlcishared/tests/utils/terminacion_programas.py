from vlcishared.flow.flow import FAILED_EXEC


def comprobar_handle_error(mock_flow_control, causa):
    mock_flow_control.handle_error.assert_called_once()
    kwargs = mock_flow_control.handle_error.call_args.kwargs
    assert causa in kwargs["cause"]


def comprobar_sys_exit_fallido(mock_sys_exit, llamadas_esperadas):
    assert mock_sys_exit.call_count == llamadas_esperadas
    for call in mock_sys_exit.call_args_list:
        assert call == ((FAILED_EXEC,), {})