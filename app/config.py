from pathlib import Path


def get_config_path():
    return Path.home() / ".PiAlarmAdapter" / "config.ini"
