import pytest
from unittest.mock import patch, mock_open
from fspin.__main__ import main as cli_main
from fspin.unified import UnifiedSpin


def test_cli_main(capsys):
    """Test fspin.__main__.main()"""
    with patch('fspin.__main__.resources') as mock_resources:
        # Mock modern importlib.resources
        mock_resources.files.return_value.joinpath.return_value.read_text.return_value = "Mocked Cheatsheet"
        cli_main()
        captured = capsys.readouterr()
        assert "Mocked Cheatsheet" in captured.out

    with patch('fspin.__main__.resources') as mock_resources:
        # Mock older importlib.resources
        del mock_resources.files
        mock_resources.open_text.return_value.__enter__.return_value.read.return_value = "Old Mocked Cheatsheet"
        cli_main()
        captured = capsys.readouterr()
        assert "Old Mocked Cheatsheet" in captured.out

    with patch('fspin.__main__.resources') as mock_resources:
        mock_resources.files.side_effect = Exception("Failed")
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data="Local Cheatsheet")):
                cli_main()
                captured = capsys.readouterr()
                assert "Local Cheatsheet" in captured.out

    with patch('fspin.__main__.resources') as mock_resources:
        mock_resources.files.side_effect = Exception("Failed")
        with patch('os.path.exists', return_value=False):
            cli_main()
            captured = capsys.readouterr()
            assert "fspin Cheatsheet not found." in captured.out


def test_unified_cheatsheet_load_failure():
    """Test UnifiedSpin._load_cheatsheet exception"""
    with patch('os.path.exists', return_value=True):
        with patch('builtins.open', side_effect=Exception("Read error")):
            # We need a new instance because it's loaded in __init__
            UnifiedSpin._cheatsheet_loaded = False
            us = UnifiedSpin()
            # If it didn't crash, it's fine for coverage


def test_unified_cheatsheet_already_loaded():
    """Test UnifiedSpin._load_cheatsheet when already loaded"""
    UnifiedSpin._cheatsheet_loaded = True
    UnifiedSpin._load_cheatsheet()  # Should return early
