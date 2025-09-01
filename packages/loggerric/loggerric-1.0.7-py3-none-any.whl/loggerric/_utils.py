from datetime import datetime

def timestamp() -> str:
    now = datetime.now()
    return f'{now.hour:02d}:{now.minute:02d}:{now.second:02d}.{str(now.microsecond)[0:min(3, len(str(now.microsecond)))]}'