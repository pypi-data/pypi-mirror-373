from colorama import Fore
from datetime import datetime

class Timestamp:
    """
    **Manage global timestamps.**
    """
    _format = '{HH}:{MI}:{SS}.{MS} T+{DH}:{DM}:{DS}.{DN}'
    _enabled = True
    _last_get = None

    @classmethod
    def get(cls, dont_override_diff:bool=False, internal_call:bool=False) -> str:
        """
        **Get the current timestamp.**

        *Parameters*:
        - `dont_override_diff` (bool): Determines whether this call updates the timestamp difference reference.
        - `internal_call` (bool): USED INTERNALLY, adds suffix space, brackets, coloring and returns timestamp even if disabled.

        *Example*:
        ```python
        ts = Timestamp.get(dont_override_diff=False)
        ```
        """
        # Check if a timestamp should be returned
        if not cls._enabled and internal_call:
            return ''

        # Grab the current time
        now = datetime.now()

        # Extract difference components
        if cls._last_get is None:
            dh = dm = ds = dn = 0
        else:
            diff = now - cls._last_get
            total_seconds = diff.total_seconds()
            dh, remainder = divmod(total_seconds, 3600)
            dm, ds = divmod(remainder, 60)
            dn = diff.microseconds // 1000

        # Lookup table for replacement loop
        lookup = {
            '{YY}': f'{now.year:04d}', '{MO}': f'{now.month:02d}', '{DD}': f'{now.day:02d}', '{HH}': f'{now.hour:02d}',
            '{MI}': f'{now.minute:02d}', '{SS}': f'{now.second:02d}', '{MS}': str(now.microsecond)[0:min(3, len(str(now.microsecond)))],
            '{DH}': f'{int(dh):02d}', '{DM}': f'{int(dm):02d}', '{DS}': f'{int(ds):02d}', '{DN}': f'{int(dn):03d}',
        }

        # If this is the first message, set diff to 0
        if cls._last_get == 0 or isinstance(cls._last_get, int):
            lookup['{DH}'] = '00'
            lookup['{DM}'] = '00'
            lookup['{DS}'] = '00'
            lookup['{dm}'] = '000'

        # Format timestamp
        timestamp = cls._format
        for k, v in lookup.items():
            timestamp = timestamp.replace(k, v)

        # Check if the difference reference should be set
        if not dont_override_diff:
            cls._last_get = now

        # Return the timestamp
        if internal_call:
            return f'{Fore.MAGENTA}[{timestamp}] {Fore.WHITE}'
        else:
            return timestamp
    
    @classmethod
    def set_format(cls, format:str) -> None:
        """
        **Specify the format of the timestamp.**

        *Parameters*:
        - `format` (str): The format of the timestamp.

        Difference = Since last timestamp (unless `dont_override_diff` is `True` in the `Timestamp.get()` function.)
        
        *Fields*:
        - `{YY}` : Year
        - `{MO}` : Month
        - `{DD}` : Day
        - `{HH}` : Hour
        - `{MI}` : Minute
        - `{SS}` : Second
        - `{MS}` : Milliseconds (3 decimals)
        - `{DH}` : Difference hours
        - `{DM}` : Difference minutes
        - `{DS}` : Difference seconds
        - `{DN}` : Difference milliseconds (3 decimals)

        *Example*:
        ```python
        Timestamp.set_format('{HH}:{MM}:{SS}')
        ```
        """
        cls._format = format

    @classmethod
    def enable(cls) -> None:
        """
        **Enable timestamps.**
        """
        cls._enabled = True
    
    @classmethod
    def disable(cls) -> None:
        """
        **Disable timestamps.**
        """
        cls._enabled = False