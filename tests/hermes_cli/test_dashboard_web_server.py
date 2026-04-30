from unittest.mock import patch

from hermes_cli import web_server


def test_dashboard_server_uses_socket_peer_for_client_address():
    with patch("uvicorn.run") as run:
        web_server.start_server(
            host="127.0.0.1",
            port=9119,
            open_browser=False,
            allow_public=False,
        )

    kwargs = run.call_args.kwargs
    assert kwargs["proxy_headers"] is False
    assert kwargs["host"] == "127.0.0.1"
    assert kwargs["port"] == 9119
