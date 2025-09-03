#!/usr/bin/env python3
"""
Tests for the pdf_font_checker.core module.
"""

import unittest
import tempfile
import os
import subprocess
from unittest.mock import patch, MagicMock
from pdf_font_checker.core import (
    list_pdf_fonts,
    _parse_mutool_fonts,
    ensure_mutool,
    _have,
    _run
)


class TestPdfFontChecker(unittest.TestCase):
    """Test cases for PDF font checking functionality."""

    def test_parse_mutool_fonts_various_formats(self):
        """Test parsing of different mutool output formats."""
        # Test output with various font name formats
        test_output = """Font 0:
name: 'Helvetica-Bold'
type: Type1
Font 1:
FontName: /TimesNewRomanPSMT
type: TrueType
Font 2:
basefont Arial-Black
Font 3:
/CalibriLight Type0
Font 4:
/Verdana-Italic CIDFontType2
"""
        expected_fonts = [
            "Helvetica-Bold",
            "TimesNewRomanPSMT", 
            "Arial-Black",
            "CalibriLight",
            "Verdana-Italic"
        ]
        
        result = _parse_mutool_fonts(test_output)
        self.assertEqual(result, expected_fonts)

    def test_parse_mutool_fonts_duplicates(self):
        """Test that duplicate font names are removed."""
        test_output = """Font 0:
name: 'Arial'
Font 1:
FontName: /Arial
Font 2:
name: 'Helvetica'
Font 3:
name: 'Arial'
"""
        expected_fonts = ["Arial", "Helvetica"]
        
        result = _parse_mutool_fonts(test_output)
        self.assertEqual(result, expected_fonts)

    def test_parse_mutool_fonts_empty(self):
        """Test parsing of empty output."""
        result = _parse_mutool_fonts("")
        self.assertEqual(result, [])

    def test_parse_mutool_fonts_no_matches(self):
        """Test parsing of output with no font information."""
        test_output = """Some other information
No font data here
Random text
"""
        result = _parse_mutool_fonts(test_output)
        self.assertEqual(result, [])

    @patch('pdf_font_checker.core._run')
    @patch('pdf_font_checker.core.ensure_mutool')
    def test_list_pdf_fonts_success(self, mock_ensure, mock_run):
        """Test successful font listing."""
        # Mock the subprocess result
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = """Font 0:
name: 'Arial-Bold'
Font 1:
FontName: /Helvetica
"""
        mock_process.stderr = ""
        mock_run.return_value = mock_process
        
        result = list_pdf_fonts("test.pdf")
        
        # Verify ensure_mutool was called
        mock_ensure.assert_called_once_with(auto_install=True)
        
        # Verify mutool was called with correct arguments
        mock_run.assert_called()
        args = mock_run.call_args[0][0]
        self.assertIn("mutool", args)
        self.assertIn("info", args)
        self.assertIn("test.pdf", args)
        
        # Verify fonts were parsed correctly
        expected_fonts = ["Arial-Bold", "Helvetica"]
        self.assertEqual(result, expected_fonts)

    @patch('pdf_font_checker.core._run')
    @patch('pdf_font_checker.core.ensure_mutool')
    def test_list_pdf_fonts_fallback_command(self, mock_ensure, mock_run):
        """Test fallback to 'mutool info' when 'mutool info -F' fails."""
        # First call (with -F) fails, second call succeeds
        mock_process_fail = MagicMock()
        mock_process_fail.returncode = 1
        mock_process_fail.stdout = ""
        mock_process_fail.stderr = "Option -F not supported"
        
        mock_process_success = MagicMock()
        mock_process_success.returncode = 0
        mock_process_success.stdout = """Font info:
name: 'TimesNewRoman'
"""
        mock_process_success.stderr = ""
        
        mock_run.side_effect = [mock_process_fail, mock_process_success]
        
        result = list_pdf_fonts("test.pdf")
        
        # Verify both commands were tried
        self.assertEqual(mock_run.call_count, 2)
        
        # Verify the result
        expected_fonts = ["TimesNewRoman"]
        self.assertEqual(result, expected_fonts)

    @patch('pdf_font_checker.core._run')
    @patch('pdf_font_checker.core.ensure_mutool')
    def test_list_pdf_fonts_failure(self, mock_ensure, mock_run):
        """Test handling of mutool command failure."""
        # Both commands fail
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_process.stdout = ""
        mock_process.stderr = "File not found"
        mock_run.return_value = mock_process
        
        with self.assertRaises(RuntimeError) as cm:
            list_pdf_fonts("nonexistent.pdf")
        
        self.assertIn("Failed to extract fonts", str(cm.exception))
        self.assertIn("File not found", str(cm.exception))

    @patch('pdf_font_checker.core._have')
    def test_ensure_mutool_already_available(self, mock_have):
        """Test ensure_mutool when mutool is already available."""
        mock_have.return_value = True
        
        # Should not raise any exception
        ensure_mutool()
        
        mock_have.assert_called_once_with("mutool")

    @patch('pdf_font_checker.core._have')
    def test_ensure_mutool_no_auto_install(self, mock_have):
        """Test ensure_mutool with auto_install disabled."""
        mock_have.return_value = False
        
        with self.assertRaises(RuntimeError) as cm:
            ensure_mutool(auto_install=False)
        
        self.assertIn("mutool not found", str(cm.exception))
        self.assertIn("auto_install is disabled", str(cm.exception))

    def test_have_command_exists(self):
        """Test _have function with existing command."""
        # Test with a command that should exist on most systems
        result = _have("python3") or _have("python")
        self.assertTrue(result)

    def test_have_command_not_exists(self):
        """Test _have function with non-existing command."""
        result = _have("nonexistent_command_12345")
        self.assertFalse(result)

    def test_run_command_success(self):
        """Test _run function with successful command."""
        result = _run(["echo", "test"])
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "test")

    def test_run_command_failure(self):
        """Test _run function with failing command."""
        result = _run(["false"])  # Command that always fails
        self.assertNotEqual(result.returncode, 0)


class TestIntegration(unittest.TestCase):
    """Integration tests that may require mutool to be installed."""

    def setUp(self):
        """Check if mutool is available for integration tests."""
        self.mutool_available = _have("mutool")

    @unittest.skipUnless(_have("mutool"), "mutool not available")
    def test_list_fonts_real_pdf(self):
        """Test with a real PDF file (if mutool is available)."""
        # Create a simple PDF with text (requires additional setup)
        # This is a placeholder for a more comprehensive integration test
        # that would require creating or having a test PDF file
        pass

    def test_integration_no_ensure(self):
        """Test list_pdf_fonts without ensuring mutool installation."""
        if not self.mutool_available:
            with self.assertRaises(RuntimeError):
                list_pdf_fonts("test.pdf", ensure=False)


if __name__ == "__main__":
    unittest.main()
