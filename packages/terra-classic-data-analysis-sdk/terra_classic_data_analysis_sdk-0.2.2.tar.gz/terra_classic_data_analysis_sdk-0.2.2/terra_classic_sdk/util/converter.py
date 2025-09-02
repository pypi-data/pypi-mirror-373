from datetime import datetime


def to_isoformat(dt: datetime) -> str:
    return (
        dt.isoformat(timespec="microseconds")
        .replace("+00:00", "Z")
        .replace(".000Z", "Z")
    )
import json

def try_json_loads(s:str):
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        return s

