import pytest

from varken.iniparser import INIParser, _validate_run_seconds


class TestUrlCheck:
    """Tests for INIParser.url_check() — URL/hostname validation."""

    def setup_method(self):
        """Create a bare INIParser instance bypassing all file I/O."""
        self.parser = object.__new__(INIParser)
        from logging import getLogger
        self.parser.logger = getLogger('test_iniparser')
        self.parser.data_folder = '/tmp'
        self.parser.config = {}
        self.parser.services = []

    def test_valid_hostname(self):
        result = self.parser.url_check('localhost', include_port=False, section='influxdb')
        assert result == 'localhost'

    def test_valid_ip(self):
        result = self.parser.url_check('192.168.1.1', include_port=False, section='test')
        assert result == '192.168.1.1'

    def test_valid_ip_with_port(self):
        result = self.parser.url_check('192.168.1.1:8989', include_port=True, section='sonarr-1')
        assert result == '192.168.1.1:8989'

    def test_valid_domain(self):
        result = self.parser.url_check('sonarr.domain.tld', include_port=False, section='sonarr-1')
        assert result == 'sonarr.domain.tld'

    def test_valid_domain_with_port(self):
        result = self.parser.url_check('sonarr.domain.tld:8989', include_port=True, section='sonarr-1')
        assert result == 'sonarr.domain.tld:8989'

    def test_valid_short_hostname(self):
        result = self.parser.url_check('sonarr', include_port=False, section='sonarr-1')
        assert result == 'sonarr'

    def test_valid_short_hostname_with_port(self):
        result = self.parser.url_check('sonarr:8989', include_port=True, section='sonarr-1')
        assert result == 'sonarr:8989'

    def test_url_with_http_scheme_raises(self):
        with pytest.raises(RuntimeError, match='Invalid URL'):
            self.parser.url_check('http://sonarr.domain.tld', include_port=False, section='sonarr-1')

    def test_url_with_https_scheme_raises(self):
        with pytest.raises(RuntimeError, match='Invalid URL'):
            self.parser.url_check('https://sonarr.domain.tld:8989', include_port=True, section='sonarr-1')


class TestValidateRunSeconds:
    """Tests for _validate_run_seconds() config guard."""

    def test_valid_typical_value(self):
        assert _validate_run_seconds(30, 'queue_run_seconds', 'sonarr-1') == 30

    def test_valid_minimum(self):
        assert _validate_run_seconds(1, 'queue_run_seconds', 'sonarr-1') == 1

    def test_valid_maximum(self):
        assert _validate_run_seconds(86400, 'queue_run_seconds', 'sonarr-1') == 86400

    def test_zero_raises(self):
        with pytest.raises(ValueError, match='must be between 1 and 86400'):
            _validate_run_seconds(0, 'queue_run_seconds', 'sonarr-1')

    def test_negative_raises(self):
        with pytest.raises(ValueError, match='must be between 1 and 86400'):
            _validate_run_seconds(-60, 'queue_run_seconds', 'sonarr-1')

    def test_above_max_raises(self):
        with pytest.raises(ValueError, match='must be between 1 and 86400'):
            _validate_run_seconds(86401, 'queue_run_seconds', 'sonarr-1')

    def test_error_message_includes_name_and_section(self):
        with pytest.raises(ValueError, match='get_activity_run_seconds'):
            _validate_run_seconds(0, 'get_activity_run_seconds', 'tautulli-1')
