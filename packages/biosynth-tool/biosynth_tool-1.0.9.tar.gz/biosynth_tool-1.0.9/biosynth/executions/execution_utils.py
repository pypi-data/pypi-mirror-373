from biosynth.algorithm.eliminate_sequence import EliminationController
from biosynth.data.app_data import EliminationData, OutputData
from biosynth.report.html_report_utils import ReportController
from biosynth.utils.display_utils import SequenceUtils
from biosynth.utils.output_utils import Logger


def is_valid_dna(sequence):
    valid_bases = set('ATCG')
    return all(base in valid_bases for base in sequence.upper())


def is_valid_patterns(patterns):
    valid_bases = set('ATCG')
    for pattern in patterns:
        if not all(base in valid_bases for base in pattern.upper()):
            return False
    return True


def is_valid_codon_usage(codon_usage):
    """
    Validates the codon usage data.

    :param codon_usage: A dictionary where keys are codons and values are dictionaries with 'aa' and 'freq'.
                        Example: {"AAA": {"aa": "K", "freq": 0.5}}
    :return: True if the codon usage data is valid, otherwise False.
    """
    valid_bases = set('ATCG')

    if len(codon_usage) != 64:
        print(len(codon_usage))
        return False

    for codon, freq in codon_usage.items():
        # Validate codon format
        if not (isinstance(codon, str) and len(codon) == 3 and all(base in valid_bases for base in codon.upper())):
            return False

        # Validate 'freq' field
        if not (isinstance(freq, (float, int)) and freq >= 0):
            return False

    return True


def is_valid_input(sequence, unwanted_patterns, codon_usage_table):
    if sequence is None:
        Logger.error(f"Target Sequence file is missing.")
        return False

    if len(sequence) == 0:
        Logger.error(f"Invalid target sequence format in file.")
        return False

    if not is_valid_dna(sequence):
        Logger.error(f"Invalid target sequence format in file.")
        return False

    if unwanted_patterns is None:
        Logger.error(f"Unwanted Patterns file is missing.")
        return False

    if len(unwanted_patterns) == 0:
        Logger.error(f"Invalid unwanted patterns format in file.")
        return False

    if not is_valid_patterns(unwanted_patterns):
        Logger.error(f"Invalid unwanted patterns format in file.")
        return False

    if codon_usage_table is None:
        Logger.error(f"Codon Usage file is missing.")
        return False

    if len(codon_usage_table) == 0:
        Logger.error(f"Invalid codon usage table format in file.")
        return False

    if not is_valid_codon_usage(codon_usage_table):
        Logger.error(f"Invalid codon usage table format in file.")
        return False

    return True


def is_valid_cost(alpha=None, beta=None, w=None):
    if not (isinstance(alpha, (int, float)) and alpha > 0):
        Logger.error(f"Invalid alpha value: α = {alpha}. Must be a positive number.")
        return False

    if not (isinstance(beta, (int, float)) and beta > 0):
        Logger.error(f"Invalid beta value: β = {beta}. Must be a positive number.")
        return False

    if not (isinstance(w, (int, float)) and w > 0):
        Logger.error(f"Invalid w value: w = {w}. Must be a positive number.")
        return False

    if alpha >= beta:
        Logger.error(f"Biological constraint violated: alpha (α = {alpha}) must be less than beta (β = {beta}).")
        return False

    if beta > w:
        Logger.error(f"Cost hierarchy violated: beta (β = {beta}) must be significantly smaller than w (w = {w}).")
        return False

    return True


def eliminate_unwanted_patterns(seq, unwanted_patterns, coding_positions):
    # Start elimination
    EliminationData.info, EliminationData.detailed_changes, OutputData.optimized_sequence, EliminationData.min_cost = EliminationController.eliminate(
        seq, unwanted_patterns, coding_positions)


def mark_non_equal_codons(input_seq, optimized_seq, coding_positions):
    # Mark non-equal codons between the original and optimized sequences
    index_seq_str, marked_input_seq, marked_optimized_seq = SequenceUtils.mark_non_equal_characters(input_seq,
                                                                                                    optimized_seq,
                                                                                                    coding_positions)
    return index_seq_str, marked_input_seq, marked_optimized_seq


def initialize_report(updated_coding_positions):
    report = ReportController(updated_coding_positions)
    return report
