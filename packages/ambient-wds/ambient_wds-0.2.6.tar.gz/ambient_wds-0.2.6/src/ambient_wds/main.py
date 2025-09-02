import os
import socket
import time
import requests
import yaml
import click

CONFIG_DIR = os.path.join(os.path.expanduser("~"), "ambient-wds")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.yaml")


def get_config_value(config, key, cli_val=None, default=None):
    if cli_val is not None:
        return cli_val
    return os.getenv(key, config.get(key, default))


def aprs_passcode_from_callsign(callsign_base):
    x = 0x73e2
    cs = callsign_base.split("-")[0]
    for i, c in enumerate(cs):
        x ^= (ord(c) << 8) if (i % 2 == 0) else ord(c)
    return x & 0x7fff


def decdeg_to_aprs(dm, is_lat=True):
    neg = dm < 0
    dm = abs(dm)
    deg = int(dm)
    minutes = (dm - deg) * 60
    hemi = ("S" if neg else "N") if is_lat else ("W" if neg else "E")
    if is_lat:
        return f"{deg:02d}{minutes:05.2f}{hemi}"
    else:
        return f"{deg:03d}{minutes:05.2f}{hemi}"


def get_ambient_latest(app_key, api_key):
    url = f"https://api.ambientweather.net/v1/devices?applicationKey={app_key}&apiKey={api_key}"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    devices = r.json()
    if not devices:
        raise RuntimeError("No devices returned from Ambient API.")
    d = devices[0]
    return d.get("lastData", {}), d.get("info", {})


def infer_position(meta):
    coords = meta.get("coords", {}) or {}
    if "coords" in coords and isinstance(coords["coords"], dict):
        coords = coords["coords"]

    lat = coords.get("lat")
    lon = coords.get("lon")
    if lat is None or lon is None:
        raise RuntimeError("No coordinates available. Set the station coordinates in Ambient Weather dashboard.")
    return float(lat), float(lon)


def inhg_to_b_tenths(inhg):
    hpa = float(inhg) * 33.8638866667
    return int(round(hpa * 10))


def f_to_t_field(temp_f):
    t = int(round(float(temp_f)))
    sign = "-" if t < 0 else ""
    return f"{sign}{abs(t):02d}"


def mph_to_3d(v):
    return f"{int(round(max(0, float(v)))):03d}"


def hum_to_2d(h):
    h = int(round(max(0, min(100, float(h)))))
    return "00" if h >= 100 else f"{h:02d}"


def inches_to_hundredths(v):
    return f"{int(round(float(v) * 100)):03d}"


def build_wx_packet(last, lat, lon):
    lat_aprs = decdeg_to_aprs(lat, True)
    lon_aprs = decdeg_to_aprs(lon, False)
    wind_dir = int(round(last.get("winddir", 0) or 0))
    wind_speed_mph = last.get("windspeedmph", 0)
    wind_gust_mph = last.get("windgustmph", wind_speed_mph)
    temp_f = last.get("tempf")
    hum = last.get("humidity")
    baro_inhg = last.get("baromabsin") or last.get("baromrelin")
    r_hour = last.get("hourlyrainin", 0)
    p_24hr = last.get("dailyrainin", 0)
    P_midnight = last.get("dailyrainin", 0)

    parts = [f"!{lat_aprs}/{lon_aprs}_"]
    parts.append(f"{wind_dir:03d}/{mph_to_3d(wind_speed_mph)}g{mph_to_3d(wind_gust_mph)}")
    if temp_f is not None:
        parts.append(f"t{f_to_t_field(temp_f)}")
    parts.append(f"r{inches_to_hundredths(r_hour)}")
    parts.append(f"p{inches_to_hundredths(p_24hr)}")
    parts.append(f"P{inches_to_hundredths(P_midnight)}")
    if hum is not None:
        parts.append(f"h{hum_to_2d(hum)}")
    if baro_inhg is not None:
        parts.append(f"b{inhg_to_b_tenths(baro_inhg):05d}")

    return "".join(parts)


def send_to_aprs_is(packet, callsign, callsign_base, aprs_passcode, server, port):
    pw = aprs_passcode or aprs_passcode_from_callsign(callsign_base)
    login = f"user {callsign_base} pass {pw} vers Ambient2APRS 1.0\n"
    line = f"{callsign}>APRS,TCPIP*:{packet}\n"
    with socket.create_connection((server, port), timeout=15) as s:
        s.sendall(login.encode("ascii"))
        s.sendall(line.encode("ascii"))


def main_loop(app_key, api_key, callsign_base, ssid, aprs_passcode, aprs_server, aprs_port, poll_seconds):
    CALLSIGN = f"{callsign_base}-{ssid}" if ssid else callsign_base
    while True:
        try:
            last, meta = get_ambient_latest(app_key, api_key)
            lat, lon = infer_position(meta)
            packet = build_wx_packet(last, lat, lon)
            send_to_aprs_is(packet, CALLSIGN, callsign_base, aprs_passcode,
                             aprs_server, aprs_port)
            print(time.strftime("%Y-%m-%d %H:%M:%S"), packet)
        except Exception as e:
            print("ERROR:", e)
        time.sleep(poll_seconds)


@click.command()
@click.option('--config-file', default=CONFIG_FILE, show_default=True, help='The YAML configuration file to use.')
@click.option("--setup", is_flag=True, help="Run interactive setup to generate config file in ~/ambient-wds/")
@click.option("--app-key", help="Ambient Weather Application Key")
@click.option("--api-key", help="Ambient Weather API Key")
@click.option("--callsign", help="APRS callsign")
@click.option("--ssid", default=13, show_default=True, help="APRS SSID")
@click.option("--aprs-passcode", default=None, help="APRS passcode")
@click.option("--aprs-server", default="noam.aprs2.net", show_default=True, help="APRS server hostname")
@click.option("--aprs-port", default=14580, show_default=True, type=int, help="APRS server port")
@click.option("--poll-seconds", default=300, show_default=True, type=int, help="Polling interval in seconds")
def main(config_file, setup, app_key, api_key, callsign, ssid, aprs_passcode, aprs_server, aprs_port, poll_seconds):

    if setup:
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)

        if os.path.exists(CONFIG_FILE):
            overwrite = click.confirm(f"{CONFIG_FILE} already exists. Overwrite?", default=False)
            if not overwrite:
                click.echo("Setup cancelled.")
                return

        ctx = click.get_current_context()
        config = {}
        for param in ctx.command.params:
            if isinstance(param, click.Option) and param.name not in ("config_file", "setup"):
                default = param.get_default(ctx)
                config[param.name.upper()] = click.prompt(
                    param.name.upper(),
                    default=default,
                    show_default=True
                )

        with open(CONFIG_FILE, "w") as f:
            yaml.safe_dump(config, f)
        click.echo(f"Config written to {CONFIG_FILE}")
        return

    config = {}
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            config = yaml.safe_load(f) or {}

    app_key = get_config_value(config, "APP_KEY", app_key)
    api_key = get_config_value(config, "API_KEY", api_key)
    callsign_base = get_config_value(config, "CALLSIGN", callsign)
    ssid = get_config_value(config, "SSID", ssid, "13")
    aprs_passcode = get_config_value(config, "APRS_PASSCODE", aprs_passcode)
    aprs_server = get_config_value(config, "APRS_SERVER", aprs_server, "noam.aprs2.net")
    aprs_port = int(get_config_value(config, "APRS_PORT", aprs_port, 14580))
    poll_seconds = int(get_config_value(config, "POLL_SECONDS", poll_seconds, 300))

    if not callsign_base or not app_key or not api_key:
        raise click.UsageError("CALLSIGN, APP_KEY, and API_KEY must be set (CLI, env, or config file)")

    main_loop(app_key, api_key, callsign_base, ssid, aprs_passcode, aprs_server, aprs_port, poll_seconds)


if __name__ == "__main__":
    main()
