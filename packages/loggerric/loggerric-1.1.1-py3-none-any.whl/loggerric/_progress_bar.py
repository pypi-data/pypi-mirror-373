from time import perf_counter
from colorama import Fore
from loggerric._utils import *
import math

class ProgressBar:
    """
    **Push a formatted progressbar to the standard output.**

    *Parameters*:
    - `end_value` (int): The end iteration number.
    - `name` (str): The name of the progressbar.
    - `bar_length` (int): The length of the progressbar.

    *Example*:
    ```python
    end_val = 50
    bar = ProgressBar(end_value=end_val, name='Progress Bar Name', bar_length=50)
    for i in range(1, end_val + 1):
        ...
        bar.update(i)
    ```
    """
    # Dunder: Initialization
    def __init__(self, end_value:int, name:str='Progress', bar_length:int=50):
        # Define class scoped variables
        self.end_value = end_value
        self.name = name
        self.bar_length = bar_length
        self._end_value_digets = len(str(end_value))
        self.start_time = 0
        self.elapsed = 0

    # Internal: Method
    def _format_time(self, seconds:float) -> str:
        # Convert seconds to hours, minutes and seconds
        seconds = int(seconds)
        h, m, s = seconds // 3600, (seconds % 3600) // 60, seconds % 60

        # Format to HH:MM:SS
        return f'{h:02d}:{m:02d}:{s:02d}'

    # Method
    def update(self, current_value:int) -> None:
        """
        **Called when the progress bar needs to update.**

        *Parameters*:
        - `current_value` (int): The current value for the progress bar.
        """
        # If its the first time called, log the start time
        if not self.start_time:
            self.start_time = perf_counter()
        
        # String formatted division 'current/end'
        division = f'{str(current_value).zfill(self._end_value_digets)}/{self.end_value}'

        # Calculate the current progress (scaled to bar length)
        progress = current_value * self.bar_length / self.end_value

        # String formatted progress bar
        bar = f'[{Fore.CYAN}{"#" * (math.floor(progress))}{"_" * (self.bar_length - math.floor(progress))}]'
        
        # String formatted percentage complete
        pct = f'{current_value * 100 / self.end_value:.2f}%'

        # Calculate the ETA
        timer = 'ETA --:--:--'
        self.elapsed = perf_counter() - self.start_time
        if current_value > 0:
            remaining = (self.elapsed / current_value) * (self.end_value - current_value)
            timer = f'ETA {self._format_time(remaining)}'

        # Log the progress bar
        print(f'{Fore.MAGENTA}[{timestamp()}] {Fore.BLUE}{self.name}: {Fore.CYAN}{division} {bar} {pct} {timer}{Fore.WHITE}', end='\n' if current_value == self.end_value else '\r')