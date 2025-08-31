from biosynth.data.app_data import InputData, CostData, OutputData
from biosynth.executions.controllers.command_controller import CommandController
from biosynth.executions.execution_utils import is_valid_input, is_valid_cost
from biosynth.utils.file_utils import SequenceReader, PatternReader, CodonUsageReader
from biosynth.utils.input_utils import ArgumentParser


class CLIController:
    def __init__(self, argv):
        self.argv = argv

    def execute(self):
        parser = ArgumentParser()

        _, s_path, p_path, c_path, o_path, alpha, beta, w = parser.parse_args(self.argv)

        seq = SequenceReader(s_path).read_sequence()
        unwanted_patterns = PatternReader(p_path).read_patterns()
        codon_usage_table = CodonUsageReader(c_path).read_codon_usage()
        codon_usage_file_name = CodonUsageReader(c_path).get_filename()

        if not is_valid_input(seq, unwanted_patterns, codon_usage_table):
            return

        InputData.dna_sequence = seq
        InputData.unwanted_patterns = unwanted_patterns
        CostData.codon_usage = codon_usage_table
        CostData.codon_usage_filename = codon_usage_file_name

        # optional values
        if alpha is not None:
            CostData.alpha = alpha

        if beta is not None:
            CostData.beta = beta

        if w is not None:
            CostData.w = w

        if not is_valid_cost(CostData.alpha, CostData.beta, CostData.w):
            return

        if o_path is not None:
            OutputData.output_path = o_path

        controller = CommandController()
        controller.run()

        return
