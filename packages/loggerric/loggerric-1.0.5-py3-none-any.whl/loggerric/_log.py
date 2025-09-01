from colorama import Fore
from loggerric._log_levels import *
from loggerric._utils import *

class Log:
    """
    **Contains various logging methods.**
    """
    # Keep track of what should be logged
    _active_levels = { LogLevel.INFO, LogLevel.WARN, LogLevel.ERROR, LogLevel.DEBUG }

    @classmethod
    def info(cls, content:str) -> None:
        """
        **Format a message as information.**

        *Parameters*:
        - `content` (str): The content you want printed.

        *Example*:
        ```python
        Log.info(content='Hello World!')
        ```
        """
        # Log the content
        if LogLevel.INFO in cls._active_levels:
            print(f'{Fore.MAGENTA}[{timestamp()}] {Fore.GREEN}[i] {content}{Fore.WHITE}')

    @classmethod
    def warn(cls, content:str) -> None:
        """
        **Format a message as a warning.**

        *Parameters*:
        - `content` (str): The content you want printed.

        *Example*:
        ```python
        Log.warn(content='Hello World!')
        ```
        """
        # Log the content
        if LogLevel.WARN in cls._active_levels:
            print(f'{Fore.MAGENTA}[{timestamp()}] {Fore.YELLOW}[w] {content}{Fore.WHITE}')

    @classmethod
    def error(cls, content:str) -> None:
        """
        **Format a message as an error.**

        *Parameters*:
        - `content` (str): The content you want printed.

        *Example*:
        ```python
        Log.error(content='Hello World!')
        ```
        """
        # Log the content
        if LogLevel.ERROR in cls._active_levels:
            print(f'{Fore.MAGENTA}[{timestamp()}] {Fore.RED}[!] {content}{Fore.WHITE}')

    @classmethod
    def debug(cls, content:str) -> None:
        """
        **Format a message as a debug message.**

        *Parameters*:
        - `content` (str): The content you want printed.

        *Example*:
        ```python
        Log.debug(content='Hello World!')
        ```
        """
        # Log the content
        if LogLevel.DEBUG in cls._active_levels:
         print(f'{Fore.MAGENTA}[{timestamp()}] {Fore.LIGHTBLACK_EX}[?] {content}{Fore.WHITE}')
    
    @classmethod
    def enable(cls, *levels:LogLevel) -> None:
        """
        **Enable logging methods.**

        *Parameters*:
        - `*levels` (LogLevel): Levels that should be enabled.

        *Example*:
        ```python
        Log.enable(LogLevel.INFO, LogLevel.WARN, ...)
        ```
        """
        cls._active_levels.update(levels)
    
    @classmethod
    def disable(cls, *levels:LogLevel) -> None:
        """
        **Disable logging methods.**

        *Parameters*:
        - `*levels` (LogLevel): Levels that should be disabled.

        *Example*:
        ```python
        Log.disable(LogLevel.INFO, LogLevel.WARN, ...)
        ```
        """
        cls._active_levels.difference_update(levels)
    
    @classmethod
    def pretty_print(cls, data, indent:int=4, depth_level:int=0, inline:bool=False) -> None:
        """
        **Print any variable so they are more readable.**

        Intended use is for dictionaries and arrays, other variables still work.

        *Parameters*:
        - `data` (any): The data you want to pretty print.
        - `indent` (int): The indentation amount for the data.
        - `depth_level` (int): USED INTERNALLY, control what child depth the recursive call is at.
        - `inline` (bool): USED INTERNALLY, keeps track of key/value printing, as to not hop to next line.

        *Example*:
        ```python
        data = {
            'name': 'John Doe',
            'age': 27,
            'skills': ['this', 'and', 'that'],
            'status': None,
            'subdict': { 'source': True, 'the_list': ['English', 'Danish'] }
        }
        Log.pretty_print(data)
        ```
        """
        spacing = ' ' * (indent * depth_level)

        # Dictionary
        if isinstance(data, dict):
            if not inline:
                print(spacing + Fore.CYAN + '{')
            else:
                print(Fore.CYAN + '{')
            for key, value in data.items():
                key_spacing = ' ' * (indent * (depth_level + 1))
                print(key_spacing + Fore.YELLOW + str(key) + Fore.WHITE + ': ', end="")
                if isinstance(value, (dict, list)):
                    cls.pretty_print(value, indent, depth_level + 1, inline=True)
                else:
                    cls.pretty_print(value, indent, depth_level + 1, inline=True)
            print(spacing + Fore.CYAN + '}')

        # List
        elif isinstance(data, list):
            if not inline:
                print(spacing + Fore.MAGENTA + '[')
            else:
                print(Fore.MAGENTA + '[')
            for item in data:
                cls.pretty_print(item, indent, depth_level + 1, inline=False)
            print(spacing + Fore.MAGENTA + ']')

        # String
        elif isinstance(data, str):
            print((spacing if not inline else "") + Fore.GREEN + f'"{data}"')

        # Number
        elif isinstance(data, (int, float, complex)):
            print((spacing if not inline else "") + Fore.BLUE + str(data))

        # Boolean
        elif isinstance(data, bool):
            print((spacing if not inline else "") + Fore.LIGHTBLUE_EX + str(data))

        # None
        elif data is None:
            print((spacing if not inline else "") + Fore.RED + 'None')

        # Other
        else:
            print((spacing if not inline else "") + Fore.WHITE + str(data))