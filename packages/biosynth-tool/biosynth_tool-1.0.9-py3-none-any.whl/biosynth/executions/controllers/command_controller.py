from datetime import datetime

from biosynth.data.app_data import InputData, EliminationData, OutputData
from biosynth.executions.execution_utils import eliminate_unwanted_patterns
from biosynth.report.html_report_utils import ReportController
from biosynth.utils.display_utils import SequenceUtils
from biosynth.utils.dna_utils import DNAUtils
from biosynth.utils.file_utils import save_file
from biosynth.utils.output_utils import Logger
from biosynth.utils.text_utils import format_text_bold_for_output

app_icon_text = """
=================================================================
=================================================================

██████╗ ██╗ ██████╗ ███████╗██╗   ██╗███╗   ██╗████████╗██╗  ██╗
██╔══██╗██║██╔═══██╗██╔════╝╚██╗ ██╔╝████╗  ██║╚══██╔══╝██║  ██║
██████╔╝██║██║   ██║███████╗ ╚████╔╝ ██╔██╗ ██║   ██║   ███████║
██╔══██╗██║██║   ██║╚════██║  ╚██╔╝  ██║╚██╗██║   ██║   ██╔══██║
██████╔╝██║╚██████╔╝███████║   ██║   ██║ ╚████║   ██║   ██║  ██║
╚═════╝ ╚═╝ ╚═════╝ ╚══════╝   ╚═╝   ╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝                                                                                                  
                                                                                                
=================================================================
=================================================================
\n
"""


class CommandController:

    def run(self):
        if not InputData.dna_sequence:
            Logger.error("The input sequence is empty, please try again")
            return

        has_overlaps, overlaps = DNAUtils.find_overlapping_regions(InputData.dna_sequence)

        if has_overlaps:
            Logger.error("The target sequence contains ORFs that share overlapping nucleotide regions:")
            Logger.space()
            Logger.info(DNAUtils.get_overlapping_regions(InputData.dna_sequence, overlaps))
            Logger.error("Please ensure the input sequence does not contain overlapping ORFs.")
            return

        Logger.notice(app_icon_text)

        # Print the target sequence
        Logger.debug(f"{format_text_bold_for_output('Target sequence:')}")
        Logger.info(f"{InputData.dna_sequence}")
        Logger.space()

        # Print the list of unwanted patterns
        Logger.debug(f"{format_text_bold_for_output('Unwanted patterns:')}")
        Logger.info(f"{SequenceUtils.get_patterns(InputData.unwanted_patterns)}")
        Logger.space()

        # Extract coding regions
        InputData.coding_positions, InputData.coding_indexes = DNAUtils.get_coding_and_non_coding_regions_positions(
            InputData.dna_sequence)

        # Handle elimination of coding regions if the user chooses to
        InputData.coding_regions_list = DNAUtils.get_coding_regions_list(InputData.coding_indexes,
                                                                         InputData.dna_sequence)

        if len(InputData.coding_indexes) > 0:
            Logger.debug('The following ORFs were identified in the target sequence:')
            Logger.info('\n'.join(f"[{key}] {value}" for key, value in InputData.coding_regions_list.items()))
            Logger.critical(
                '\nAll ORFs are assumed to be coding regions. If you wish to exclude some ORFs, then please use the GUI.')
        else:
            Logger.critical("No ORFs were identified in the provided target sequence.")

        # Eliminate unwanted patterns
        eliminate_unwanted_patterns(InputData.dna_sequence, InputData.unwanted_patterns, InputData.coding_positions)

        Logger.notice(format_text_bold_for_output('\n' + '_' * 90 + '\n'))
        Logger.info(EliminationData.info)
        Logger.notice(format_text_bold_for_output('\n' + '_' * 90 + '\n'))

        Logger.debug(format_text_bold_for_output('Optimized Sequence:'))
        Logger.info(OutputData.optimized_sequence)
        Logger.space()

        changes = '\n'.join(EliminationData.detailed_changes) if EliminationData.detailed_changes else None
        Logger.debug(format_text_bold_for_output('Detailed substitutions relative to the target sequence:'))
        Logger.info(f"{changes}")
        Logger.space()

        # Save the results
        report = ReportController(InputData.coding_positions)

        Logger.critical("Preparing files for export...\n")
        file_date = datetime.today().strftime("%d-%b-%Y_%H-%M-%S")
        report.create_report(file_date)
        path = report.download_report(OutputData.output_path)
        Logger.notice(path)

        filename = f"Optimized Sequence - {file_date}.txt"
        path = save_file(OutputData.optimized_sequence, filename, OutputData.output_path)
        Logger.notice(path)
        Logger.space()

        Logger.critical("All files were exported successfully.")
        Logger.space()
