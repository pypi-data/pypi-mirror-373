import pytest
from unittest.mock import patch
from enhance_this import clipboard
from rich.console import Console

@pytest.fixture
def mock_pyperclip_copy():
    with patch('pyperclip.copy') as mock_copy:
        yield mock_copy

@pytest.fixture
def mock_console_print():
    with patch.object(Console, 'print') as mock_print:
        yield mock_print

def test_copy_to_clipboard_success(mock_pyperclip_copy, mock_console_print):
    test_text = "This is a test string"
    clipboard.copy_to_clipboard(test_text)
    mock_pyperclip_copy.assert_called_once_with(test_text)
    mock_console_print.assert_called_once_with("[green]✔[/green] Enhanced prompt copied to clipboard.")

def test_copy_to_clipboard_failure(mock_pyperclip_copy, mock_console_print):
    mock_pyperclip_copy.side_effect = clipboard.pyperclip.PyperclipException("Copy failed")
    test_text = "This is a test string"
    clipboard.copy_to_clipboard(test_text)
    mock_pyperclip_copy.assert_called_once_with(test_text)
    mock_console_print.assert_called_once_with("[yellow]⚠[/yellow] Could not copy to clipboard. `xclip` or `xsel` may be required on Linux.")
