"""
Entry point for running biosynth as a module: python -m biosynth
"""

import sys

from biosynth.BioSynth import BioSynthApp


def main():
    """Main entry point for the biosynth CLI command."""
    BioSynthApp.execute(sys.argv[1:])


if __name__ == "__main__":
    main()
