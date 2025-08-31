import sys
import unittest
from io import StringIO
from unittest.mock import patch

from biosynth.utils.input_utils import ArgumentParser


class TestCommandLineParser(unittest.TestCase):
    def setUp(self):
        self.parser = ArgumentParser()

    def test_parse_args(self):
        # Simulate command-line arguments
        sys.argv = ["test.py", "-p", "files/mult_coding/p_file.txt", "-s", "files/mult_coding/s_file.txt", "-c",
                    "files/codon_usage_table/kazuza_chloroplast.txt", "-a", "2.0", "-b", "3.0", "-w", "200.0"]

        gui, s_file, p_file, c_file, o_file, alpha, beta, w = self.parser.parse_args(sys.argv[1:])

        # Check if parsing arguments works correctly
        self.assertEqual((gui, s_file, p_file, c_file, o_file, alpha, beta, w),
                         (False, "files/mult_coding/s_file.txt", "files/mult_coding/p_file.txt",
                          "files/codon_usage_table/kazuza_chloroplast.txt", None, 2.0, 3.0, 200.0))

    @patch('sys.stderr', new_callable=StringIO)
    def assert_stderr(self, expected_output, mock_stderr):
        self.parser.parse_args(["invalid"])
        self.assertEqual(mock_stderr.getvalue().strip(), expected_output)
