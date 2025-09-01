"""Tests for novus_pytils.utils.console module."""

import pytest
from unittest.mock import patch, MagicMock, call
import sys
from io import StringIO

from novus_pytils.utils.console import (
    ColorCode, print_color, print_success, print_error, print_warning, print_info,
    print_table, print_progress_bar, confirm_action, get_user_input, clear_screen, move_cursor
)


class TestColorCode:
    """Test the ColorCode enum."""
    
    def test_color_code_values(self):
        assert ColorCode.BLACK.value == '\033[30m'
        assert ColorCode.RED.value == '\033[31m'
        assert ColorCode.GREEN.value == '\033[32m'
        assert ColorCode.YELLOW.value == '\033[33m'
        assert ColorCode.BLUE.value == '\033[34m'
        assert ColorCode.MAGENTA.value == '\033[35m'
        assert ColorCode.CYAN.value == '\033[36m'
        assert ColorCode.WHITE.value == '\033[37m'
        assert ColorCode.RESET.value == '\033[0m'


class TestPrintColor:
    """Test the print_color function."""
    
    @patch('builtins.print')
    @patch('novus_pytils.utils.console._detect_color_support', return_value=True)
    def test_print_color_with_support(self, mock_detect, mock_print):
        print_color("Hello", ColorCode.RED)
        mock_print.assert_called_once()
        args, kwargs = mock_print.call_args
        assert ColorCode.RED.value in args[0]
        assert ColorCode.RESET.value in args[0]
        assert "Hello" in args[0]
    
    @patch('builtins.print')
    @patch('novus_pytils.utils.console._detect_color_support', return_value=False)
    def test_print_color_without_support(self, mock_detect, mock_print):
        print_color("Hello", ColorCode.RED)
        mock_print.assert_called_once_with("Hello")
    
    @patch('builtins.print')
    @patch('novus_pytils.utils.console._detect_color_support', return_value=True)
    def test_print_color_with_background(self, mock_detect, mock_print):
        print_color("Hello", ColorCode.RED, background=ColorCode.WHITE)
        mock_print.assert_called_once()
        args, kwargs = mock_print.call_args
        assert ColorCode.RED.value in args[0]
        assert "47m" in args[0]  # White background code
        assert "Hello" in args[0]


class TestPrintSuccess:
    """Test the print_success function."""
    
    @patch('novus_pytils.utils.console.print_color')
    def test_print_success(self, mock_print_color):
        print_success("Success message")
        mock_print_color.assert_called_once_with("Success message", ColorCode.GREEN)


class TestPrintError:
    """Test the print_error function."""
    
    @patch('novus_pytils.utils.console.print_color')
    def test_print_error(self, mock_print_color):
        print_error("Error message")
        mock_print_color.assert_called_once_with("Error message", ColorCode.RED)


class TestPrintWarning:
    """Test the print_warning function."""
    
    @patch('novus_pytils.utils.console.print_color')
    def test_print_warning(self, mock_print_color):
        print_warning("Warning message")
        mock_print_color.assert_called_once_with("Warning message", ColorCode.YELLOW)


class TestPrintInfo:
    """Test the print_info function."""
    
    @patch('novus_pytils.utils.console.print_color')
    def test_print_info(self, mock_print_color):
        print_info("Info message")
        mock_print_color.assert_called_once_with("Info message", ColorCode.CYAN)


class TestPrintTable:
    """Test the print_table function."""
    
    @patch('builtins.print')
    def test_print_simple_table(self, mock_print):
        headers = ["Name", "Age"]
        rows = [["John", "30"], ["Jane", "25"]]
        
        print_table(headers, rows)
        
        # Should print header, separator, and rows
        assert mock_print.call_count >= 3
    
    @patch('builtins.print')
    def test_print_table_with_custom_separator(self, mock_print):
        headers = ["Name", "Age"]
        rows = [["John", "30"]]
        
        print_table(headers, rows, separator=" | ")
        
        mock_print.assert_called()
        # Check that custom separator is used
        calls = mock_print.call_args_list
        assert any(" | " in str(call) for call in calls)
    
    @patch('builtins.print')
    def test_print_table_with_alignment(self, mock_print):
        headers = ["Name", "Age"]
        rows = [["John", "30"], ["Jane", "25"]]
        
        print_table(headers, rows, align_right=['Age'])
        
        mock_print.assert_called()
    
    @patch('builtins.print')
    def test_empty_table(self, mock_print):
        print_table([], [])
        mock_print.assert_called()


class TestPrintProgressBar:
    """Test the print_progress_bar function."""
    
    @patch('sys.stdout.write')
    @patch('sys.stdout.flush')
    def test_progress_bar_beginning(self, mock_flush, mock_write):
        print_progress_bar(0, 100)
        mock_write.assert_called()
        mock_flush.assert_called()
    
    @patch('sys.stdout.write')
    @patch('sys.stdout.flush')
    def test_progress_bar_middle(self, mock_flush, mock_write):
        print_progress_bar(50, 100)
        mock_write.assert_called()
        mock_flush.assert_called()
    
    @patch('sys.stdout.write')
    @patch('sys.stdout.flush')
    def test_progress_bar_complete(self, mock_flush, mock_write):
        print_progress_bar(100, 100)
        mock_write.assert_called()
        mock_flush.assert_called()
        # Should print newline at completion
        calls = [str(call) for call in mock_write.call_args_list]
        assert any('\\n' in call for call in calls)
    
    @patch('sys.stdout.write')
    @patch('sys.stdout.flush')
    def test_progress_bar_with_prefix_suffix(self, mock_flush, mock_write):
        print_progress_bar(50, 100, prefix="Loading", suffix="Complete")
        mock_write.assert_called()
        calls = [str(call) for call in mock_write.call_args_list]
        assert any("Loading" in call for call in calls)
        assert any("Complete" in call for call in calls)


class TestConfirmAction:
    """Test the confirm_action function."""
    
    @patch('builtins.input', return_value='y')
    def test_confirm_action_yes(self, mock_input):
        result = confirm_action("Continue?")
        assert result is True
        mock_input.assert_called_once_with("Continue? [y/N]: ")
    
    @patch('builtins.input', return_value='n')
    def test_confirm_action_no(self, mock_input):
        result = confirm_action("Continue?")
        assert result is False
    
    @patch('builtins.input', return_value='')
    def test_confirm_action_default_false(self, mock_input):
        result = confirm_action("Continue?", default=False)
        assert result is False
    
    @patch('builtins.input', return_value='')
    def test_confirm_action_default_true(self, mock_input):
        result = confirm_action("Continue?", default=True)
        assert result is True
    
    @patch('builtins.input', return_value='Y')
    def test_confirm_action_uppercase(self, mock_input):
        result = confirm_action("Continue?")
        assert result is True
    
    @patch('builtins.input', return_value='yes')
    def test_confirm_action_full_word(self, mock_input):
        result = confirm_action("Continue?")
        assert result is True


class TestGetUserInput:
    """Test the get_user_input function."""
    
    @patch('builtins.input', return_value='user input')
    def test_get_user_input_basic(self, mock_input):
        result = get_user_input("Enter value:")
        assert result == "user input"
        mock_input.assert_called_once_with("Enter value: ")
    
    @patch('builtins.input', return_value='')
    def test_get_user_input_with_default(self, mock_input):
        result = get_user_input("Enter value:", default="default")
        assert result == "default"
    
    @patch('builtins.input', side_effect=['', 'valid input'])
    def test_get_user_input_required(self, mock_input):
        result = get_user_input("Enter value:", required=True)
        assert result == "valid input"
        assert mock_input.call_count == 2
    
    @patch('builtins.input', side_effect=['invalid', 'valid'])
    def test_get_user_input_with_validator(self, mock_input):
        def validator(value):
            return value == 'valid'
        
        result = get_user_input("Enter value:", validator=validator)
        assert result == "valid"
        assert mock_input.call_count == 2


class TestClearScreen:
    """Test the clear_screen function."""
    
    @patch('os.system')
    def test_clear_screen_system_method(self, mock_system):
        clear_screen(method='system')
        mock_system.assert_called_once_with('cls' if sys.platform == 'win32' else 'clear')
    
    @patch('sys.stdout.write')
    @patch('sys.stdout.flush')
    def test_clear_screen_ansi_method(self, mock_flush, mock_write):
        clear_screen(method='ansi')
        mock_write.assert_called_once_with('\033[2J\033[H')
        mock_flush.assert_called_once()
    
    def test_clear_screen_invalid_method(self):
        with pytest.raises(ValueError):
            clear_screen(method='invalid')


class TestMoveCursor:
    """Test the move_cursor function."""
    
    @patch('sys.stdout.write')
    @patch('sys.stdout.flush')
    def test_move_cursor(self, mock_flush, mock_write):
        move_cursor(10, 5)
        mock_write.assert_called_once_with('\033[5;10H')
        mock_flush.assert_called_once()
    
    @patch('sys.stdout.write')
    @patch('sys.stdout.flush')
    def test_move_cursor_origin(self, mock_flush, mock_write):
        move_cursor(1, 1)
        mock_write.assert_called_once_with('\033[1;1H')
        mock_flush.assert_called_once()