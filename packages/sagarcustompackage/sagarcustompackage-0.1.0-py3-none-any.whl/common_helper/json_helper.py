from datetime import datetime, date, time 
from datetime import timedelta

def convert_to_json_compatible(data):
    if isinstance(data, dict):
        return {k: convert_to_json_compatible(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_to_json_compatible(item) for item in data]
    elif isinstance(data, (datetime, date, time)):
        return data.isoformat()
    elif isinstance(data, timedelta):  
        return str(data)
    elif isinstance(data, (int, float, str)):  # Basic types
        return data
    elif isinstance(data, bytes):
        return data.decode('utf-8')
    elif isinstance(data, bytearray):
        return data.decode('utf-8')
    elif isinstance(data, memoryview):
        return data.tobytes()
    elif isinstance(data, set):
        return list(data)
    elif isinstance(data, frozenset):
        return list(data)