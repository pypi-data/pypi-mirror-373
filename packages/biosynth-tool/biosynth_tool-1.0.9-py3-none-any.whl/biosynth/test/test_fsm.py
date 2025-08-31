import unittest

from biosynth.algorithm.fsm import FSM


class TestCalculateFSM(unittest.TestCase):
    def setUp(self):
        # Mock data for testing
        self.alphabet = {'A', 'C', 'G', 'T'}
        self.unwanted_patterns = {'ATATCA', 'TAGTAC'}

    def test_fsm_transitions(self):
        fsm = FSM(self.unwanted_patterns, self.alphabet)
        expected_transitions = {('AA', 'A'): 'AA',
                                ('AA', 'C'): 'AC',
                                ('AA', 'G'): 'AG',
                                ('AA', 'T'): 'AT',

                                ('AC', 'A'): 'CA',
                                ('AC', 'C'): 'CC',
                                ('AC', 'G'): 'CG',
                                ('AC', 'T'): 'CT',

                                ('AG', 'A'): 'GA',
                                ('AG', 'C'): 'GC',
                                ('AG', 'G'): 'GG',
                                ('AG', 'T'): 'GT',

                                ('AT', 'A'): 'ATA',
                                ('AT', 'C'): 'TC',
                                ('AT', 'G'): 'TG',
                                ('AT', 'T'): 'TT',

                                ('CA', 'A'): 'AA',
                                ('CA', 'C'): 'AC',
                                ('CA', 'G'): 'AG',
                                ('CA', 'T'): 'AT',

                                ('CC', 'A'): 'CA',
                                ('CC', 'C'): 'CC',
                                ('CC', 'G'): 'CG',
                                ('CC', 'T'): 'CT',

                                ('CG', 'A'): 'GA',
                                ('CG', 'C'): 'GC',
                                ('CG', 'G'): 'GG',
                                ('CG', 'T'): 'GT',

                                ('CT', 'A'): 'TA',
                                ('CT', 'C'): 'TC',
                                ('CT', 'G'): 'TG',
                                ('CT', 'T'): 'TT',

                                ('GA', 'A'): 'AA',
                                ('GA', 'C'): 'AC',
                                ('GA', 'G'): 'AG',
                                ('GA', 'T'): 'AT',

                                ('GC', 'A'): 'CA',
                                ('GC', 'C'): 'CC',
                                ('GC', 'G'): 'CG',
                                ('GC', 'T'): 'CT',

                                ('GG', 'A'): 'GA',
                                ('GG', 'C'): 'GC',
                                ('GG', 'G'): 'GG',
                                ('GG', 'T'): 'GT',

                                ('GT', 'A'): 'TA',
                                ('GT', 'C'): 'TC',
                                ('GT', 'G'): 'TG',
                                ('GT', 'T'): 'TT',

                                ('TA', 'A'): 'AA',
                                ('TA', 'C'): 'AC',
                                ('TA', 'G'): 'TAG',
                                ('TA', 'T'): 'AT',

                                ('TC', 'A'): 'CA',
                                ('TC', 'C'): 'CC',
                                ('TC', 'G'): 'CG',
                                ('TC', 'T'): 'CT',

                                ('TG', 'A'): 'GA',
                                ('TG', 'C'): 'GC',
                                ('TG', 'G'): 'GG',
                                ('TG', 'T'): 'GT',

                                ('TT', 'A'): 'TA',
                                ('TT', 'C'): 'TC',
                                ('TT', 'G'): 'TG',
                                ('TT', 'T'): 'TT',

                                ('ATA', 'A'): 'AA',
                                ('ATA', 'C'): 'AC',
                                ('ATA', 'G'): 'TAG',
                                ('ATA', 'T'): 'ATAT',

                                ('ATAT', 'A'): 'ATA',
                                ('ATAT', 'C'): 'ATATC',
                                ('ATAT', 'G'): 'TG',
                                ('ATAT', 'T'): 'TT',

                                ('ATATC', 'A'): None,
                                ('ATATC', 'C'): 'CC',
                                ('ATATC', 'G'): 'CG',
                                ('ATATC', 'T'): 'CT',

                                ('TAG', 'A'): 'GA',
                                ('TAG', 'C'): 'GC',
                                ('TAG', 'G'): 'GG',
                                ('TAG', 'T'): 'TAGT',

                                ('TAGT', 'A'): 'TAGTA',
                                ('TAGT', 'C'): 'TC',
                                ('TAGT', 'G'): 'TG',
                                ('TAGT', 'T'): 'TT',

                                ('TAGTA', 'A'): 'AA',
                                ('TAGTA', 'C'): None,
                                ('TAGTA', 'G'): 'TAG',
                                ('TAGTA', 'T'): 'AT'}

        self.assertTrue(len(fsm.V) == 22)
        self.assertTrue(len(fsm.f) == len(fsm.V) * len(fsm.sigma))

        for key, expected_value in expected_transitions.items():
            if fsm.f[key] != expected_value:
                self.fail(f"FSM transition mismatches:\n{(key, expected_value)}")
