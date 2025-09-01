"""Console utility functions for terminal output.

This module provides functions for creating progress bars and other console output utilities.
"""
import os
import sys
from typing import List, Optional
from enum import Enum

class ColorCode(Enum):
    """ANSI color codes for terminal output."""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BLACK = '\033[30m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def _detect_color_support() -> bool:
    """
    Detect if the terminal supports colors.
    
    Returns:
        bool: True if colors are supported, False otherwise.
    """
    # Check if stdout is a TTY
    if not sys.stdout.isatty():
        return False
    
    # Check environment variables
    if os.environ.get('COLORTERM'):
        return True
        
    term = os.environ.get('TERM', '').lower()
    if 'color' in term or 'xterm' in term:
        return True
        
    return False

# Global variable to control color output
COLORS_ENABLED = _detect_color_support()



def print_color(text: str, color: ColorCode, background: Optional[ColorCode] = None, **kwargs) -> None:
    """
    Print text in the specified color.

    Args:
        text (str): The text to print.
        color (ColorCode): The color to use.
        background (ColorCode, optional): The background color to use.
        **kwargs: Additional arguments to pass to print().
    """
    if COLORS_ENABLED:
        if background:
            formatted_text = f"{color.value}{background.value}{text}{ColorCode.RESET.value}"
        else:
            formatted_text = f"{color.value}{text}{ColorCode.RESET.value}"
        print(formatted_text, **kwargs)
    else:
        print(text, **kwargs)


def print_success(text: str) -> None:
    """
    Print success message in green.

    Args:
        text (str): The success message to print.
    """
    print_color(f"✓ {text}", ColorCode.GREEN)

def print_error(text: str) -> None:
    """
    Print error message in red.

    Args:
        text (str): The error message to print.
    """
    print_color(f"✗ {text}", ColorCode.RED)

def print_warning(text: str) -> None:
    """
    Print warning message in yellow.

    Args:
        text (str): The warning message to print.
    """
    print_color(f"⚠ {text}", ColorCode.YELLOW)

def print_info(text: str) -> None:
    """
    Print info message in blue.

    Args:
        text (str): The info message to print.
    """
    print_color(f"ℹ {text}", ColorCode.BLUE)

def print_table(headers: List[str], rows: List[List[str]], separator: str = '|', 
                alignments: Optional[List[str]] = None, header_color: Optional[ColorCode] = None) -> None:
    """
    Print a formatted table.

    Args:
        headers (List[str]): The table headers.
        rows (List[List[str]]): The table rows.
        separator (str): The column separator.
        alignments (List[str], optional): Column alignments ('left', 'center', 'right').
        header_color (ColorCode, optional): Color for headers.
    """
    if not headers:
        return

    # Calculate column widths
    col_widths = [len(header) for header in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))

    # Print headers
    header_cells = []
    for i, header in enumerate(headers):
        if alignments and i < len(alignments):
            if alignments[i] == 'center':
                formatted_header = header.center(col_widths[i])
            elif alignments[i] == 'right':
                formatted_header = header.rjust(col_widths[i])
            else:
                formatted_header = header.ljust(col_widths[i])
        else:
            formatted_header = header.ljust(col_widths[i])
        header_cells.append(f" {formatted_header} ")
    
    header_row = separator.join(header_cells)
    if header_color and COLORS_ENABLED:
        print(f"{header_color.value}{header_row}{ColorCode.RESET.value}")
    else:
        print(header_row)
    print('-' * len(header_row))

    # Print rows
    for row in rows:
        row_cells = []
        for i, cell in enumerate(row):
            if alignments and i < len(alignments):
                if alignments[i] == 'center':
                    formatted_cell = str(cell).center(col_widths[i])
                elif alignments[i] == 'right':
                    formatted_cell = str(cell).rjust(col_widths[i])
                else:
                    formatted_cell = str(cell).ljust(col_widths[i])
            else:
                formatted_cell = str(cell).ljust(col_widths[i])
            row_cells.append(f" {formatted_cell} ")
        row_str = separator.join(row_cells)
        print(row_str)

def print_progress_bar(iteration: int, total: int, prefix: str = '', suffix: str = '', 
                      decimals: int = 1, length: int = 100, width: Optional[int] = None, 
                      fill: str = '█', print_end: str = "\r") -> None:
    """
    Create terminal progress bar.

    Args:
        iteration (int): Current iteration.
        total (int): Total iterations.
        prefix (str): Prefix string.
        suffix (str): Suffix string.
        decimals (int): Number of decimals in percent complete.
        length (int): Character length of bar (deprecated, use width).
        width (int, optional): Character length of bar.
        fill (str): Bar fill character.
        print_end (str): End character.
    """
    # Use width if provided, otherwise use length
    bar_length = width if width is not None else length
    
    # Handle division by zero
    if total == 0:
        percent = "0"
        filled_length = 0
    else:
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filled_length = int(bar_length * iteration // total)
    
    bar = fill * filled_length + '-' * (bar_length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=print_end)
    if iteration == total:
        print()

def confirm_action(message: str, default: bool = False) -> bool:
    """
    Ask user for confirmation.

    Args:
        message (str): The confirmation message.
        default (bool): Default response if user just presses Enter.

    Returns:
        bool: True if user confirms, False otherwise.
    """
    while True:
        prompt = f"{message} [{'Y/n' if default else 'y/N'}]: "
        response = input(prompt).strip().lower()
        
        if not response:
            return default
        if response in ['y', 'yes', 'true', '1']:
            return True
        elif response in ['n', 'no', 'false', '0']:
            return False
        # If response is invalid, loop again

def get_user_input(prompt: str, default: str = None, required: bool = False, validator=None) -> str:
    """
    Get user input with optional default value and validation.

    Args:
        prompt (str): The input prompt.
        default (str): Default value if user just presses Enter.
        required (bool): Whether input is required.
        validator: Optional validation function that returns True if input is valid.

    Returns:
        str: The user input.
    """
    while True:
        display_prompt = f"{prompt}"
        if default:
            display_prompt += f" [{default}]"
        if not display_prompt.endswith(": ") and not display_prompt.endswith(":"):
            display_prompt += ": "
        
        response = input(display_prompt).strip()
        
        if not response and default:
            response = default
        elif not response and required:
            print_error("Input is required. Please try again.")
            continue
        elif not response:
            return response
            
        # Validate input if validator is provided
        if validator and not validator(response):
            print_error("Invalid input. Please try again.")
            continue
            
        return response

def clear_screen(method: str = 'system') -> None:
    """
    Clear the terminal screen.
    
    Args:
        method (str): Method to use ('system' or 'ansi').
    """
    if method == 'ansi':
        print('\033[2J\033[H', end='')
    else:
        import platform
        if platform.system() == 'Windows':
            os.system('cls')
        else:
            os.system('clear')

def move_cursor(x: int, y: int) -> None:
    """
    Move cursor to specified position.

    Args:
        x (int): Column position.
        y (int): Row position.
    """
    print(f"\033[{y};{x}H", end='')
