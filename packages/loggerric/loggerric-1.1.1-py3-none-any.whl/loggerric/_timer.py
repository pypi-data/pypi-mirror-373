from time import perf_counter
from colorama import Fore
from loggerric._utils import *

class Timer:
    """
    **Time how long a code snippet takes to execute.**

    *Arguments*:
    - `name` (str): Name of the timer.

    *Example*:
    ```python
    with Timer(name='Timer Name'):
        ...
    ```
    """
    # Dunder: Initialization
    def __init__(self, name:str='Timer'):        
        # Define class scoped variables
        self.name = name
        self.end_time = 0
        self.elapsed = 0

    # Dunder: Entering 'with' operator
    def __enter__(self):
        # Log the start time in variable, and log to STDIO
        self.start_time = perf_counter()
        print(f'{Fore.MAGENTA}[{timestamp()}] {Fore.BLUE}{self.name}: {Fore.CYAN}Started...{Fore.WHITE}')

    # Dunder: Exiting 'with' operator
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Log the end time, and calculate the time elapsed
        self.end_time = perf_counter()
        self.elapsed = self.end_time - self.start_time

        # Check if duration should be converted to milliseconds
        is_ms = False
        if self.elapsed < 1:
            is_ms = True
            self.elapsed *= 1_000
        
        # Log the duration
        print(f'{Fore.MAGENTA}[{timestamp()}] {Fore.BLUE}{self.name}: {Fore.CYAN}Finished... {Fore.YELLOW}{self.elapsed:,.5f} {"ms" if is_ms else "s"}{Fore.CYAN} Elapsed.{Fore.WHITE}')