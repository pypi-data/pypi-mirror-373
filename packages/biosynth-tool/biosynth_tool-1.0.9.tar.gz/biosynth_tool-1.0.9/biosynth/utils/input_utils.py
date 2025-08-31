import getopt
import sys

from biosynth.utils.output_utils import Logger
from biosynth.utils.text_utils import format_text_bold_for_output
from biosynth.utils.text_utils import set_output_format, OutputFormat
from biosynth.utils.info_utils import get_info_usage, get_elimination_info

try:
    from importlib.metadata import version as package_version
    VERSION = package_version("biosynth-tool")
except ImportError:
    # importlib.metadata not available (older Python)
    VERSION = "1.0.0-local"
except Exception:
    # fallback if the package isn't installed yet
    VERSION = "1.0.0-local"

def get_terminal_usage():
    return f"\n{format_text_bold_for_output('Usage:')}\n" \
           "\t$ biosynth -s <seq_file_path> -p <pattern_file_path> -o <output_path_dir> -c <codon_usage_file> [-g] [-a <alpha>] [-b <beta>] [-w <w>]\n\n" \
           "\tThis application is designed for the elimination of unwanted patterns from synthetic DNA sequences.\n\n"

def get_terminal_options():
    return f"{format_text_bold_for_output('Options:')}\n" \
           "\t-g --gui                  Option to run the program via user interface. If using this option, there is no need to specify any -s, -p, or -o options.\n" \
           "\t-s --target_sequence      Specifies the sequence file path (mandatory)\n" \
           "\t-p --unwanted_patterns    Specifies the unwanted patterns file path (mandatory)\n" \
           "\t-c --codon_usage          Specifies the codon usage table file path (mandatory). This parameter allows the program to prioritize codon usage based on the provided table.\n" \
           "\t-o --out_dir              Specifies the output directory path (optional - default is the downloads directory)\n" \
           "\t-a --alpha                Specifies the value for transition substitution cost (optional - default is 1.0)\n" \
           "\t-b --beta                 Specifies the value for transversion substitution cost (optional - default is 2.0)\n" \
           "\t-w --non_synonymous_w     Specifies the value for non-synonymous substitution cost (optional - default is 100.0)\n\n"

def get_terminal_information():
    return f"{format_text_bold_for_output('Information:')}\n" \
           f"{get_info_usage()}\n" \
           f"{get_elimination_info()}"

class ArgumentParser:
    def __init__(self):
        self.gui = False

        self.s_path = None
        self.p_path = None
        self.c_path = None
        self.o_path = None
        self.alpha = None
        self.beta = None
        self.w = None

    def parse_args(self, argv):
        """
        Parses command-line arguments and extracts file paths from them.

        Parameters:
            argv (list): List of command-line arguments.

        Returns:
            tuple: A tuple containing the paths to the patterns file and sequence file, and a flag for GUI.
        """
        try:
            opts, args = getopt.getopt(argv, "hs:p:c:o:ga:b:w:v",
                                       ["help", "target_sequence=", "unwanted_patterns=", "codon_usage=", "out_dir=",
                                        "gui", "alpha=", "beta=", "non_synonymous_w=", "version"])
        except getopt.GetoptError as err:
            set_output_format(OutputFormat.TERMINAL)
            Logger.error(
                f"The specified argument is not valid: {err}. "
                f"For assistance, please use the help option '--help' or '-h' to review the accepted parameters."
            )
            sys.exit(2)

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                set_output_format(OutputFormat.TERMINAL)
                Logger.help(get_terminal_usage())
                Logger.help(get_terminal_options())
                Logger.help(get_terminal_information())
                sys.exit(1)
            elif opt in ("-v", "--version"):
                set_output_format(OutputFormat.TERMINAL)
                Logger.info(f"BioSynth version {VERSION}")
                sys.exit(0)
            elif opt in ("-g", "--gui"):
                self.gui = True
                break
            elif opt in ("-s", "--target_sequence"):
                self.s_path = arg
            elif opt in ("-p", "--unwanted_patterns"):
                self.p_path = arg
            elif opt in ("-c", "--codon_usage"):
                self.c_path = arg
            elif opt in ("-a", "--alpha"):
                self.alpha = float(arg)  # Ensure alpha is treated as a float
            elif opt in ("-b", "--beta"):
                self.beta = float(arg)  # Ensure beta is treated as a float
            elif opt in ("-w", "--non_synonymous_w"):
                self.w = float(arg)  # Ensure w is treated as a float
            elif opt in ("-o", "--out_dir"):
                self.o_path = arg


        return self.gui, self.s_path, self.p_path, self.c_path, self.o_path, self.alpha, self.beta, self.w
