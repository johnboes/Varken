import pytest

from varken.structures import (
    InfluxServer, SonarrServer, RadarrServer, TautulliServer,
    OmbiServer, SickChillServer, UniFiServer
)


class TestInfluxServer:
    def test_defaults(self):
        s = InfluxServer()
        assert s.port == 8086
        assert s.ssl is False
        assert s.verify_ssl is False
        assert s.token == ''
        assert s.org == ''
        assert s.url == 'localhost'

    def test_custom_values(self):
        s = InfluxServer(url='influxdb', port=9999, token='mytoken', org='myorg', ssl=True)
        assert s.url == 'influxdb'
        assert s.port == 9999
        assert s.token == 'mytoken'
        assert s.org == 'myorg'
        assert s.ssl is True

    def test_immutable(self):
        s = InfluxServer()
        with pytest.raises(AttributeError):
            s.port = 1234


class TestSonarrServer:
    def test_defaults(self):
        s = SonarrServer()
        assert s.missing_days == 0
        assert s.future_days == 0
        assert s.queue is False
        assert s.queue_run_seconds == 30
        assert s.missing_days_run_seconds == 30
        assert s.future_days_run_seconds == 30

    def test_custom_values(self):
        s = SonarrServer(id=1, url='http://sonarr:8989', api_key='abc', queue=True)
        assert s.id == 1
        assert s.queue is True
        assert s.api_key == 'abc'


class TestRadarrServer:
    def test_defaults(self):
        s = RadarrServer()
        assert s.get_missing is False
        assert s.queue is False

    def test_custom_values(self):
        s = RadarrServer(id=1, url='http://radarr:7878', api_key='xyz', get_missing=True)
        assert s.get_missing is True


class TestTautulliServer:
    def test_defaults(self):
        s = TautulliServer()
        assert s.get_activity is False
        assert s.get_stats is False
        assert s.get_activity_run_seconds == 30
        assert s.get_stats_run_seconds == 30


class TestSickChillServer:
    def test_defaults(self):
        s = SickChillServer()
        assert s.get_missing is False
        assert s.verify_ssl is False


class TestUniFiServer:
    def test_defaults(self):
        s = UniFiServer()
        assert s.get_usg_stats_run_seconds == 30
        assert s.verify_ssl is False
