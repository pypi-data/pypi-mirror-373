import sys
from typing import NoReturn
from cptool_py.UI import print_error, print_warning

def error_message(message: str) -> None:
    print_error(f'Error: {message}')

def fatal_error_message(message: str) -> NoReturn:
    print_error(f'ERROR: {message}')
    sys.exit(1)

def warning_message(message: str) -> None:
    print_warning(f'Warning: {message}')

