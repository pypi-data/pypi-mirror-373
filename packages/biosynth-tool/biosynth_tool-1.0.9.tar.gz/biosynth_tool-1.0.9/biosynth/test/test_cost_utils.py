import unittest
from unittest.mock import patch

import numpy as np

from biosynth.utils.cost_utils import calculate_cost


class TestCalculateCost(unittest.TestCase):
    def setUp(self):
        # Mock data for testing
        self.target_sequence = "ATAATGCTTACGTAA"  # "NNN" for non-coding regions
        self.coding_positions = [0, 0, 0, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2,
                                 3]  # Adjusted codon positions: 1, 2, 3 for each codon
        self.codon_usage = {
            "TAC": 0.2,
            "GTA": 0.5,
            "CGT": 0.1,
            "TTA": 0.1,
            "CTT": 0.1,  # synonymous codon for Leucine
            "TAG": 0.01,  # stop codon
        }

        self.alpha = 1.0
        self.beta = 2.0
        self.w = 5.0

    @patch("biosynth.utils.amino_acid_utils.AminoAcidConfig")
    def test_non_coding_transition(self, MockAminoAcidConfig):
        MockAminoAcidConfig.is_transition.return_value = True
        _, cost = calculate_cost(self.target_sequence, self.coding_positions, self.codon_usage, 0, "", "G", self.alpha,
                                 self.beta, self.w)
        self.assertEqual(cost, self.alpha)

    @patch("biosynth.utils.amino_acid_utils.AminoAcidConfig")
    def test_non_coding_transversion(self, MockAminoAcidConfig):
        MockAminoAcidConfig.is_transition.return_value = False
        _, cost = calculate_cost(self.target_sequence, self.coding_positions, self.codon_usage, 0, "", "C", self.alpha,
                                 self.beta, self.w)
        self.assertEqual(cost, self.beta)

    def test_no_substitution(self):
        _, cost = calculate_cost(self.target_sequence, self.coding_positions, self.codon_usage, 0, "", "A", self.alpha,
                                 self.beta, self.w)
        self.assertEqual(cost, 0.0)

    @patch("biosynth.utils.amino_acid_utils.AminoAcidConfig")
    def test_synonymous_substitution(self, MockAminoAcidConfig):
        MockAminoAcidConfig.get_last3.return_value = "CTT"  # Simulate the codon at the position
        MockAminoAcidConfig.get_last2.return_value = "CT"  # Partial codon setup (just for setup)
        MockAminoAcidConfig.encodes_same_amino_acid.return_value = True  # Indicate that it's a synonymous substitution
        _, cost = calculate_cost(self.target_sequence, self.coding_positions, self.codon_usage, 8, "CTT", "A",
                                 self.alpha,
                                 self.beta, self.w)
        self.assertAlmostEqual(cost, -np.log10(self.codon_usage["TTA"]))

    @patch("biosynth.utils.amino_acid_utils.AminoAcidConfig")
    def test_stop_codon_formation(self, MockAminoAcidConfig):
        MockAminoAcidConfig.get_last3.return_value = "ATG"  # Valid stop codon
        MockAminoAcidConfig.get_last2.return_value = "TG"  # Partial codon (just for setup)
        MockAminoAcidConfig.either_is_stop_codon.return_value = True  # This should confirm it's a stop codon
        _, cost = calculate_cost(self.target_sequence, self.coding_positions, self.codon_usage, 5, "ATG", "A",
                                 self.alpha,
                                 self.beta, self.w)
        self.assertEqual(cost, float("inf"))

    @patch("biosynth.utils.amino_acid_utils.AminoAcidConfig")
    def test_stop_codon_substitution(self, MockAminoAcidConfig):
        MockAminoAcidConfig.get_last3.return_value = "TAA"  # Valid stop codon
        MockAminoAcidConfig.get_last2.return_value = "TC"  # Partial codon (just for setup)
        MockAminoAcidConfig.either_is_stop_codon.return_value = True  # This should confirm it's a stop codon
        _, cost = calculate_cost(self.target_sequence, self.coding_positions, self.codon_usage, 14, "TAC", "A",
                                 self.alpha,
                                 self.beta, self.w)
        self.assertEqual(cost, float("inf"))

    @patch("biosynth.utils.amino_acid_utils.AminoAcidConfig")
    def test_non_synonymous_substitution(self, MockAminoAcidConfig):
        MockAminoAcidConfig.get_last3.return_value = "CGT"
        MockAminoAcidConfig.get_last2.return_value = "CG"
        MockAminoAcidConfig.encodes_same_amino_acid.return_value = False
        MockAminoAcidConfig.either_is_stop_codon.return_value = False
        _, cost = calculate_cost(self.target_sequence, self.coding_positions, self.codon_usage, 8, "CGT", "A",
                                 self.alpha,
                                 self.beta, self.w)
        self.assertEqual(cost, self.w)

    def test_out_of_bounds_index(self):
        with self.assertRaises(IndexError):
            calculate_cost(self.target_sequence, self.coding_positions, self.codon_usage, 20, "", "A", self.alpha,
                           self.beta, self.w)

    def test_invalid_codon_usage(self):
        invalid_codon_usage = {"TAC": -0.1}  # Invalid probability
        with self.assertRaises(ValueError):
            calculate_cost(self.target_sequence, self.coding_positions, invalid_codon_usage, 8, "", "A", self.alpha,
                           self.beta, self.w)
