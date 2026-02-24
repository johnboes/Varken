from unittest.mock import MagicMock, patch
from requests.exceptions import SSLError, ConnectionError, InvalidSchema

from varken.helpers import boolcheck, hashit, rfc1918_ip_check, connection_handler


class TestBoolcheck:
    def test_true_values(self):
        assert boolcheck('true') is True
        assert boolcheck('True') is True
        assert boolcheck('yes') is True

    def test_false_values(self):
        assert boolcheck('false') is False
        assert boolcheck('no') is False
        assert boolcheck('0') is False
        assert boolcheck('') is False


class TestHashit:
    def test_returns_32_char_hex(self):
        result = hashit('test')
        assert len(result) == 32
        assert all(c in '0123456789abcdef' for c in result)

    def test_deterministic(self):
        assert hashit('hello') == hashit('hello')

    def test_different_inputs_differ(self):
        assert hashit('a') != hashit('b')


class TestRfc1918IpCheck:
    def test_private_ips(self):
        assert rfc1918_ip_check('192.168.1.1') is True
        assert rfc1918_ip_check('10.0.0.1') is True
        assert rfc1918_ip_check('172.16.0.1') is True

    def test_public_ips(self):
        assert rfc1918_ip_check('8.8.8.8') is False
        assert rfc1918_ip_check('1.1.1.1') is False


class TestConnectionHandler:
    def _make_session(self, status_code=200, json_data=None, raise_exc=None):
        session = MagicMock()
        request = MagicMock()
        request.url = 'http://test.local/api'
        if raise_exc:
            session.send.side_effect = raise_exc
        else:
            response = MagicMock()
            response.status_code = status_code
            response.json.return_value = json_data or {}
            session.send.return_value = response
        return session, request

    def test_returns_json_on_200(self):
        session, request = self._make_session(200, {'key': 'value'})
        result = connection_handler(session, request, verify=True)
        assert result == {'key': 'value'}

    def test_returns_false_on_401(self):
        session, request = self._make_session(401)
        session.send.return_value.content = b'Unauthorized'
        result = connection_handler(session, request, verify=True)
        assert result is False

    def test_returns_false_on_404(self):
        session, request = self._make_session(404)
        result = connection_handler(session, request, verify=True)
        assert result is False

    def test_ssl_error_returns_false(self):
        session, request = self._make_session(raise_exc=SSLError('ssl error'))
        result = connection_handler(session, request, verify=True)
        assert result is False

    def test_connection_error_returns_false(self):
        session, request = self._make_session(raise_exc=ConnectionError('no route'))
        result = connection_handler(session, request, verify=True)
        assert result is False

    def test_ssl_verify_false_suppresses_warning(self):
        session, request = self._make_session(200, {})
        with patch('varken.helpers.disable_warnings') as mock_dw:
            connection_handler(session, request, verify=False)
            mock_dw.assert_called_once()

    def test_ssl_verify_true_no_suppress(self):
        session, request = self._make_session(200, {})
        with patch('varken.helpers.disable_warnings') as mock_dw:
            connection_handler(session, request, verify=True)
            mock_dw.assert_not_called()
