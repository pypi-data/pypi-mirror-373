import time
import unittest

from biosynth.executions.controllers.debug_controller import DebugController
from biosynth.utils.file_utils import delete_dir
from biosynth.utils.output_utils import Logger
from biosynth.utils.text_utils import OutputFormat, set_output_format


def execute_unittests():
    loader = unittest.TestLoader()
    start_dir = 'biosynth/test/'
    suite = loader.discover(start_dir)

    runner = unittest.TextTestRunner()
    runner.run(suite)


if __name__ == "__main__":
    try:
        delete_dir('output')

        # DEBUG
        execute_unittests()
        time.sleep(2.2)
        set_output_format(OutputFormat.TERMINAL)
        DebugController.execute()

    except KeyboardInterrupt:
        Logger.error("\nProgram stopped by the user.")
