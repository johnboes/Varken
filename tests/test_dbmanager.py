from datetime import datetime, timezone

from influxdb_client import Point

from varken.dbmanager import _dict_to_point


class TestDictToPoint:
    def test_measurement_name(self):
        d = {'measurement': 'Tautulli', 'tags': {}, 'fields': {'count': 1}}
        p = _dict_to_point(d)
        assert isinstance(p, Point)
        assert 'Tautulli' in p.to_line_protocol()

    def test_tags_included(self):
        d = {'measurement': 'test', 'tags': {'server': '1', 'type': 'session'}, 'fields': {'count': 1}}
        lp = _dict_to_point(d).to_line_protocol()
        assert 'server=1' in lp
        assert 'type=session' in lp

    def test_none_tag_skipped(self):
        d = {'measurement': 'test', 'tags': {'valid': 'yes', 'missing': None}, 'fields': {'count': 1}}
        lp = _dict_to_point(d).to_line_protocol()
        assert 'valid=yes' in lp
        assert 'missing' not in lp

    def test_integer_field(self):
        d = {'measurement': 'test', 'tags': {}, 'fields': {'stream_count': 3}}
        lp = _dict_to_point(d).to_line_protocol()
        assert 'stream_count=3' in lp

    def test_string_field(self):
        d = {'measurement': 'test', 'tags': {}, 'fields': {'hash': 'abc123'}}
        lp = _dict_to_point(d).to_line_protocol()
        assert 'hash="abc123"' in lp

    def test_time_preserved(self):
        t = datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        d = {'measurement': 'test', 'tags': {}, 'fields': {'v': 1}, 'time': t}
        lp = _dict_to_point(d).to_line_protocol()
        assert lp is not None
        assert '1717243200' in lp

    def test_no_time_key(self):
        d = {'measurement': 'test', 'tags': {}, 'fields': {'v': 1}}
        p = _dict_to_point(d)
        assert p is not None

    def test_empty_tags_dict(self):
        d = {'measurement': 'test', 'tags': {}, 'fields': {'v': 1}}
        lp = _dict_to_point(d).to_line_protocol()
        assert 'test' in lp

    def test_full_tautulli_payload(self):
        d = {
            'measurement': 'Tautulli',
            'tags': {'type': 'current_stream_stats', 'server': 1},
            'time': '2024-01-01T00:00:00',
            'fields': {
                'stream_count': 0,
                'total_bandwidth': 0,
                'wan_bandwidth': 0,
                'lan_bandwidth': 0,
            }
        }
        lp = _dict_to_point(d).to_line_protocol()
        assert 'Tautulli' in lp
        assert 'stream_count=0' in lp
