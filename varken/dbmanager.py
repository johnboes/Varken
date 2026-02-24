from sys import exit
from logging import getLogger
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


def _dict_to_point(record):
    p = Point(record['measurement'])
    for tag, value in record.get('tags', {}).items():
        if value is not None:
            p = p.tag(tag, value)
    for field, value in record.get('fields', {}).items():
        p = p.field(field, value)
    if 'time' in record:
        p = p.time(record['time'])
    return p


class DBManager(object):
    def __init__(self, server):
        self.server = server
        self.logger = getLogger()
        if self.server.url == "influxdb.domain.tld":
            self.logger.critical("You have not configured your varken.ini. Please read Wiki page for configuration")
            exit()

        scheme = 'https' if self.server.ssl else 'http'
        url = f"{scheme}://{self.server.url}:{self.server.port}"

        self.influx = InfluxDBClient(
            url=url,
            token=self.server.token,
            org=self.server.org,
            verify_ssl=self.server.verify_ssl
        )
        self._write_api = self.influx.write_api(write_options=SYNCHRONOUS)
        self._buckets_api = self.influx.buckets_api()

        try:
            health = self.influx.health()
            self.logger.info('InfluxDB status: %s (version: %s)', health.status, health.version)
        except Exception as e:
            self.logger.critical("Error testing connection to InfluxDB. Please check your url/hostname: %s", e)
            exit(1)

        found_buckets = self._buckets_api.find_buckets().buckets or []
        bucket_names = [b.name for b in found_buckets]

        if 'varken' not in bucket_names:
            self.logger.info("Creating varken bucket")
            self._buckets_api.create_bucket(bucket_name='varken', org=self.server.org)

    def write_points(self, data):
        d = data
        self.logger.debug('Writing Data to InfluxDB %s', d)
        try:
            points = [_dict_to_point(record) for record in d]
            self._write_api.write(bucket='varken', org=self.server.org, record=points)
        except Exception as e:
            self.logger.error('Error writing data to influxdb. Dropping this set of data. '
                              'Check your database! Error: %s', e)
