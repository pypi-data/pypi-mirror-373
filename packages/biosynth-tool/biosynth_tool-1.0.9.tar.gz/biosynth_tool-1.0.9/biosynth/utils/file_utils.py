import os
import re
import shutil
import sys
from pathlib import Path

from biosynth.utils.output_utils import Logger


def read_codon_freq_file(raw_lines, convert_to_dna=True):
    """
    Reads a codon-frequency file with 2 columns: codon and frequency.

    :param raw_lines: Path to file (e.g., codon_usage_chloroplast.txt)
    :param convert_to_dna: If True, replaces 'U' with 'T' in codons (RNA to DNA).
    :return: Dictionary {codon: frequency}
    """
    codon_usage = {}

    for line in raw_lines:
        line = line.strip()
        parts = line.split()
        if len(parts) != 2:
            raise ValueError(f"Invalid line format: {line}")

        codon = parts[0].upper()
        if convert_to_dna:
            codon = codon.replace('U', 'T')
        try:
            freq = float(parts[1])
        except ValueError:
            raise ValueError(f"Invalid frequency value: {parts[1]} in line: {line}")

        codon_usage[codon] = freq

    return codon_usage


# Define a base class for reading data from a file.
class FileDataReader:
    def __init__(self, file_path):
        """
        Initializes a FileDataReader object.

        :param file_path: Path to the file to be read.
        """
        self.file_path = file_path

    def read_lines(self):
        """
        Reads the lines from the specified file.

        :return: A list containing the lines read from the file.
        """
        with open(self.file_path, 'r') as file:
            return file.readlines()

# Inherit from FileDataReader to read sequences from a file.
class SequenceReader(FileDataReader):
    def read_sequence(self):
        """
        Reads a sequence from the file, removing leading/trailing whitespace.

        :return: A string representing a sequence, or None if no valid sequence is found.
        """

        if self.file_path is None:
            return None

        raw_seq = self.read_lines()
        for line in raw_seq:
            if line.isspace():
                continue
            return line.strip()
        return None


# Inherit from FileDataReader to read patterns from a file.
class PatternReader(FileDataReader):
    def read_patterns(self):
        """
        Reads patterns from the file, splitting them by commas and adding to a set.

        :return: A set containing the extracted patterns.
        """

        if self.file_path is None:
            return None

        res = set()
        raw_patterns = self.read_lines()
        for line in raw_patterns:
            if line.isspace():
                continue
            patterns = line.strip().split(',')
            res.update(patterns)
        return res


# Inherit from FileDataReader to read the codon usage table from a file.
class CodonUsageReader(FileDataReader):
    def read_codon_usage(self):
        """
        Reads the codon usage table from the file and parses it into a dictionary.

        :return: A dictionary where keys are codons and values are dictionaries with frequency and epsilon.
        """
        if self.file_path is None:
            return None

        raw_lines = self.read_lines()
        return read_codon_freq_file(raw_lines)

    def get_filename(self):
        """
        Returns the name of the file (excluding the path).

        :return: Filename as a string.
        """
        return os.path.basename(self.file_path)


def create_dir(directory):
    try:
        os.makedirs(directory, exist_ok=True)
    except OSError as error:
        return f"Creation of the directory '{directory}' failed because of {error}"


def delete_dir(directory):
    try:
        shutil.rmtree(directory)
    except OSError as error:
        return f"Deleting of the directory '{directory}' failed because of {error}"


def save_file(output, filename, path=None):
    try:
        # Convert path to Path object if it's not None
        if path:
            output_path = Path(path) / 'BioSynth Outputs'
        else:
            downloads_path = Path.home() / 'Downloads'
            output_path = downloads_path / 'BioSynth Outputs'

        # Replace colons with underscores in the filename
        filename = re.sub(':', '_', filename)
        base_name = filename.split('-')[0].strip()

        # Create the directory if it doesn't exist
        create_dir(output_path)

        # Save the file
        output_file_path = output_path / filename
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write(output)

        return f"* {base_name} has been saved to:\n  {output_file_path}\n"

    except FileNotFoundError:
        return "An error occurred while saving the file - File not found."
    except PermissionError:
        return "An error occurred while saving the file - Permission denied."
    except IsADirectoryError:
        return "An error occurred while saving the file - the specified path is a directory, not a file."
    except Exception as e:
        return f"An error occurred while saving the file - {e}"


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    else:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
