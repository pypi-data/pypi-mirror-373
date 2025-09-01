RED = '\033[91m'
BOLD = '\033[1m'

def _with_format(message: str, format_codes: str) -> str:
    return f'{format_codes}{message}\033[00m' # Resets after the message.

def print_error(message: str) -> None:
    print(_with_format(message, RED+BOLD))

def print_warning(message: str) -> None:
    print(_with_format(message, RED))

def confirm(message: str) -> bool:
    while True:
        response = input(f'{message} (y/n) ').lower()
        if response == 'y': return True
        elif response == 'n': return False
        print('Invalid response.')

