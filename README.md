<p align="center">
<img width="800" src="https://raw.githubusercontent.com/Boerderij/Varken/master/assets/varken_full_banner.jpg" alt="Logo Banner">
</p>

[![pipeline status](https://img.shields.io/github/actions/workflow/status/johnboes/Varken/varken.yml?style=flat-square)](https://github.com/johnboes/Varken/actions)
[![Release](https://img.shields.io/github/release/boerderij/varken.svg?style=flat-square)](https://github.com/Boerderij/Varken/releases/latest)

> **Fork of [Boerderij/Varken](https://github.com/Boerderij/Varken)** — modernised for InfluxDB 2.x, Python 3.11, and production container hardening.

Dutch for PIG. PIG is an Acronym for Plex/InfluxDB/Grafana

Varken is a standalone application to aggregate data from the Plex
ecosystem into InfluxDB using Grafana for a frontend

Requirements:
* [Python 3.11+](https://www.python.org/downloads/)
* [Python3-pip](https://pip.pypa.io/en/stable/installing/)
* [InfluxDB 2.x](https://www.influxdata.com/)
* [Grafana](https://grafana.com/)

<p align="center">
Example Dashboard

<img width="800" src="https://i.imgur.com/3hNZTkC.png" alt="dashboard">
</p>

Supported Modules:
* [Sonarr](https://sonarr.tv/) - Smart PVR for newsgroup and bittorrent users.
* [SickChill](https://sickchill.github.io/) - SickChill is an automatic Video Library Manager for TV Shows.
* [Radarr](https://radarr.video/) - A fork of Sonarr to work with movies à la Couchpotato.
* [Tautulli](https://tautulli.com/) - A Python based monitoring and tracking tool for Plex Media Server.
* [Ombi](https://ombi.io/) - Want a Movie or TV Show on Plex or Emby? Use Ombi!
* [Lidarr](https://lidarr.audio/) - Looks and smells like Sonarr but made for music.

Key features:
* Multiple server support for all modules
* Geolocation mapping from [GeoLite2](https://dev.maxmind.com/geoip/geoip2/geolite2/)
* Grafana [Worldmap Panel](https://grafana.com/plugins/grafana-worldmap-panel/installation) support


---

## Changes in this fork

### InfluxDB 2.x migration
The upstream project used the legacy `influxdb` Python client (v1 API). This fork migrates to `influxdb-client` (v2 API) with token/org-based authentication. The `[influxdb]` config section now uses `token` and `org` instead of `username` and `password`. Varken creates its own bucket on first run.

### Container hardening
- Runs as a non-root `varken` user (UID/GID 1000) — no longer runs as root
- `python3` is PID 1 via an `entrypoint.sh` wrapper so `SIGTERM`/`SIGINT` from `docker stop` reach the process directly
- `DEBUG` defaults to `false` (upstream defaulted to `true`)

### Graceful shutdown
`SIGTERM` and `SIGINT` are handled explicitly — the job scheduler is cleared cleanly before exit, preventing mid-write interruptions on `docker stop` or container restart.

### Retry/backoff on connection errors
`connection_handler` retries transient `ConnectionError` and `ChunkedEncodingError` failures up to 3 times with exponential backoff (1 s, 2 s). Non-retryable errors (`SSLError`, `InvalidSchema`) fail immediately.

### SSL warning handling
Removed the global `disable_warnings(InsecureRequestWarning)` that suppressed all SSL errors unconditionally. Warnings are now only suppressed when `verify_ssl = false` is explicitly set, and a debug log message is emitted.

### Config validation
All `*_run_seconds` values are validated at startup. Values outside the range 1–86400 raise an error immediately with a clear message rather than failing silently at runtime.

### Security fixes
- All `exit()` calls inside library modules replaced with `raise RuntimeError` so failures propagate correctly and the process is testable
- Hardcoded UniFi default credentials (`ubnt`/`ubnt`) removed — `username` and `password` now default to `None` and must be set explicitly
- Public IP lookup endpoint changed from `http://ip.42.pl/raw` (HTTP, unreliable) to `https://api.ipify.org`
- InfluxDB tokens are masked in all log output

### Pinned dependencies
`requirements.txt` pins `requests`, `influxdb-client`, and `urllib3` to specific versions for deterministic builds.

### Test suite
54 tests covering `dbmanager`, `helpers`, `structures`, and `iniparser` — run with `pytest`.

---

## Installation

### Docker (recommended)

```yaml
version: '3'
networks:
  internal:
    driver: bridge
services:
  varken:
    hostname: varken
    container_name: varken
    image: ghcr.io/johnboes/varken:latest
    networks:
      - internal
    volumes:
      - /path/to/varken/config:/config
    environment:
      - TZ=America/Chicago
      - VRKN_GLOBAL_SONARR_SERVER_IDS=1
      - VRKN_GLOBAL_RADARR_SERVER_IDS=1
      - VRKN_GLOBAL_LIDARR_SERVER_IDS=false
      - VRKN_GLOBAL_TAUTULLI_SERVER_IDS=1
      - VRKN_GLOBAL_OMBI_SERVER_IDS=false
      - VRKN_GLOBAL_SICKCHILL_SERVER_IDS=false
      - VRKN_GLOBAL_UNIFI_SERVER_IDS=false
      - VRKN_GLOBAL_MAXMIND_LICENSE_KEY=xxxxxxxxxxxxxxxx
      - VRKN_INFLUXDB_URL=influxdb.domain.tld
      - VRKN_INFLUXDB_PORT=8086
      - VRKN_INFLUXDB_SSL=false
      - VRKN_INFLUXDB_VERIFY_SSL=false
      - VRKN_INFLUXDB_TOKEN=your-influxdb-v2-token
      - VRKN_INFLUXDB_ORG=your-org
      - VRKN_TAUTULLI_1_URL=tautulli.domain.tld:8181
      - VRKN_TAUTULLI_1_FALLBACK_IP=1.1.1.1
      - VRKN_TAUTULLI_1_APIKEY=xxxxxxxxxxxxxxxx
      - VRKN_TAUTULLI_1_SSL=false
      - VRKN_TAUTULLI_1_VERIFY_SSL=false
      - VRKN_TAUTULLI_1_GET_ACTIVITY=true
      - VRKN_TAUTULLI_1_GET_ACTIVITY_RUN_SECONDS=30
      - VRKN_TAUTULLI_1_GET_STATS=true
      - VRKN_TAUTULLI_1_GET_STATS_RUN_SECONDS=3600
      - VRKN_SONARR_1_URL=sonarr.domain.tld:8989
      - VRKN_SONARR_1_APIKEY=xxxxxxxxxxxxxxxx
      - VRKN_SONARR_1_SSL=false
      - VRKN_SONARR_1_VERIFY_SSL=false
      - VRKN_SONARR_1_MISSING_DAYS=7
      - VRKN_SONARR_1_MISSING_DAYS_RUN_SECONDS=300
      - VRKN_SONARR_1_FUTURE_DAYS=1
      - VRKN_SONARR_1_FUTURE_DAYS_RUN_SECONDS=300
      - VRKN_SONARR_1_QUEUE=true
      - VRKN_SONARR_1_QUEUE_RUN_SECONDS=300
      - VRKN_RADARR_1_URL=radarr.domain.tld
      - VRKN_RADARR_1_APIKEY=xxxxxxxxxxxxxxxx
      - VRKN_RADARR_1_SSL=false
      - VRKN_RADARR_1_VERIFY_SSL=false
      - VRKN_RADARR_1_QUEUE=true
      - VRKN_RADARR_1_QUEUE_RUN_SECONDS=300
      - VRKN_RADARR_1_GET_MISSING=true
      - VRKN_RADARR_1_GET_MISSING_RUN_SECONDS=300
    restart: unless-stopped
```

### ini file

Place `varken.ini` in your `/config` volume. See [`data/varken.example.ini`](data/varken.example.ini) for a full reference. The `[influxdb]` section requires `token` and `org` (v2 API):

```ini
[influxdb]
url = influxdb.domain.tld
port = 8086
ssl = false
verify_ssl = false
token = your-influxdb-v2-token-here
org = your-org-name
```

> **Migrating from upstream?** Replace `username`/`password` in your `[influxdb]` config with `token` and `org`. Generate a token in the InfluxDB UI under **Data → Tokens**.

---

## Running tests

```bash
pip install -r requirements-test.txt
pytest
```

---

## Upstream

Original project: [Boerderij/Varken](https://github.com/Boerderij/Varken)
Upstream installation guides: [wiki.cajun.pro](https://wiki.cajun.pro/books/varken/chapter/installation)
