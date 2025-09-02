from datetime import datetime

def get_timestamp_now_as_string(include_ms:bool = False):
    if include_ms:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
    else:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")