from colorama import Fore
from loggerric._timestamp import *

def prompt(question:str, options:list[str]=[], default:str=None, loop_until_valid:bool=False, case_sensitive:bool=True) -> str | None:
    """
    **Prompts standard I/O and returns the answer.**

    If options are given but not chosen by the user during prompting, return value will be `None`

    *Parameters*:
    - `question` (str): The question appearing in the prompt.
    - `options` (list[str]): Options that the user can pick from during prompting.
    - `default` (str): If options are not `None`, optionally specify a default value.
    - `loop_until_valid` (bool): Loop the prompting until the users answer is in the options parameter.
    - `case_sensitive` (bool): Weather or not the answer (with options) is case sensitive.

    *Example (No Options)*:
    ```python
    answer = prompt(question='Insert your name')
    ```

    *Example (Options)*:
    ```python
    answer = prompt(question="What's the best?", options=['a', 'b', 'c'], default='b', loop_until_valid=True, case_sensitive=False)
    ```
    """
    # If no options ommitted prompt immediately
    if len(options) == 0:
        return input(f'{Timestamp.get(internal_call=True)}{Fore.BLUE}{question}: {Fore.CYAN}') or None

    # Format options
    options_formatted = f'{Fore.BLUE} | '.join(Fore.YELLOW + o for o in options)
    
    # Lower case if not case sensitive
    if not case_sensitive:
        options = [o.lower() for o in options]

    # Prompt user
    answer = ''
    while (answer if case_sensitive else answer.lower()) not in options:
        answer = input(f'{Timestamp.get(internal_call=True)}{Fore.BLUE}{question} [ {options_formatted}{Fore.BLUE} ]{f" ({Fore.YELLOW}{default}{Fore.BLUE})" if default else ""}:{Fore.CYAN} ')

        if not loop_until_valid:
            break

        if default != None:
            break

        # If the answer is invalid, tell the user
        if (answer if case_sensitive else answer.lower()) not in options:
            print(f'{Timestamp.get(internal_call=True)}{Fore.RED}Invalid Option: "{Fore.YELLOW}{answer}{Fore.RED}"{Fore.WHITE}')

    # Validate answer
    if len(answer) == 0 and default != None:
        return default
    if (answer if case_sensitive else answer.lower()) in options:
        return answer
    
    # Implementor decides what to happen if user answers "wrong"
    return None