from enum import Enum

from biosynth.utils.output_utils import Logger


class OutputFormat(Enum):
    NONE = 0
    TERMINAL = 1
    GUI = 2


output_format = OutputFormat.NONE


def set_output_format(o_format):
    global output_format
    try:
        output_format = o_format
    except KeyError:
        Logger.error("Invalid output format. Supported formats: 'NONE', 'TERMINAL', and 'GUI'.")


def format_text_bold_for_output(text):
    if output_format == OutputFormat.TERMINAL:
        return f"\033[1m{text}\033[0m"
    elif output_format == OutputFormat.GUI:
        return f"<b>{text}</b>"
    else:
        Logger.error("Invalid output format. Supported formats: 'TERMINAL' and 'GUI'.")
        return ""
