codon_to_amino_acid = {
    'TTT': 'F',
    'TTC': 'F',  # Phenylalanine (F)
    'TTA': 'L',
    'TTG': 'L',  # Leucine (L)
    'CTT': 'L',
    'CTC': 'L',
    'CTA': 'L',
    'CTG': 'L',  # Leucine (L)
    'ATT': 'I',
    'ATC': 'I',
    'ATA': 'I',  # Isoleucine (I)
    'ATG': 'M',  # Methionine (M) (Start codon)
    'GTT': 'V',
    'GTC': 'V',
    'GTA': 'V',
    'GTG': 'V',  # Valine (V)
    'TCT': 'S',
    'TCC': 'S',
    'TCA': 'S',
    'TCG': 'S',  # Serine (S)
    'CCT': 'P',
    'CCC': 'P',
    'CCA': 'P',
    'CCG': 'P',  # Proline (P)
    'ACT': 'T',
    'ACC': 'T',
    'ACA': 'T',
    'ACG': 'T',  # Threonine (T)
    'GCT': 'A',
    'GCC': 'A',
    'GCA': 'A',
    'GCG': 'A',  # Alanine (A)
    'TAT': 'Y',
    'TAC': 'Y',  # Tyrosine (Y)
    'CAT': 'H',
    'CAC': 'H',  # Histidine (H)
    'CAA': 'Q',
    'CAG': 'Q',  # Glutamine (Q)
    'AAT': 'N',
    'AAC': 'N',  # Asparagine (N)
    'AAA': 'K',
    'AAG': 'K',  # Lysine (K)
    'GAT': 'D',
    'GAC': 'D',  # Aspartic acid (D)
    'GAA': 'E',
    'GAG': 'E',  # Glutamic acid (E)
    'TGT': 'C',
    'TGC': 'C',  # Cysteine (C)
    'TGG': 'W',  # Tryptophan (W)
    'CGT': 'R',
    'CGC': 'R',
    'CGA': 'R',
    'CGG': 'R',  # Arginine (R)
    'AGT': 'S',
    'AGC': 'S',  # Serine (S)
    'AGA': 'R',
    'AGG': 'R',  # Arginine (R)
    'GGT': 'G',
    'GGC': 'G',
    'GGA': 'G',
    'GGG': 'G',  # Glycine (G)
    'TGA': '*',
    'TAA': '*',
    'TAG': '*'  # Stop codon (*)
}


class AminoAcidConfig:

    @staticmethod
    def get_last2(v):
        """
        Extracts the last two bases associated with the FSM state v.

        Parameters:
            v (str): FSM state representation as a string.

        Returns:
            str: Last two bases of the state v.
        """
        # Assuming v contains a string representation of the bases (e.g., "ACGT")
        if len(v) < 2:
            raise ValueError("Length of v must contains at least 2 bases.")

        return v[-2:]

    @staticmethod
    def get_last3(target_sequence, i):
        """
        Extracts the last three bases in the target sequence ending at position i.

        Parameters:
            target_sequence (str): The full target sequence as a string.
            i (int): Position in the target sequence (0-based index).

        Returns:
            str: Last three bases ending at position i.
        """
        if i < 2:
            raise ValueError("Position i must be at least 2 to extract the last three bases.")

        return target_sequence[i - 2:i + 1]

    @staticmethod
    def encodes_same_amino_acid(proposed_codon, current_codon):
        """
        Checks if two codons encode the same amino acid.

        Args:
            proposed_codon (str): The codon to be tested.
            current_codon (str): The current codon.

        Returns:
            bool: True if both codons encode the same amino acid, False otherwise.
        """
        return codon_to_amino_acid.get(proposed_codon) == codon_to_amino_acid.get(current_codon)

    @staticmethod
    def either_is_stop_codon(current_codon, proposed_codon):
        """
        Checks if a given codon is a stop codon.

        Args:
            current_codon (str): The original codon.
            proposed_codon (str): The codon to be tested.

        Returns:
            bool: True if the codon is a stop codon, False otherwise.
        """
        return codon_to_amino_acid.get(current_codon) == '*' or codon_to_amino_acid.get(proposed_codon) == '*'

    @staticmethod
    def is_start_codon(codon_position):
        """
        Checks if a given codon is a stop codon.

        Args:
            codon_position (number): The codon to be tested, should be always -3

        Returns:
            bool: True if the codon is a start codon, False otherwise.
        """
        return codon_position == -3

    @staticmethod
    def is_transition(nucleotide1, nucleotide2):
        """
        Checks if the substitution between two nucleotides is a transition mutation.

        Args:
            nucleotide1 (str): The original nucleotide (A, C, G, or T).
            nucleotide2 (str): The proposed nucleotide (A, C, G, or T).

        Returns:
            bool: True if the substitution is a transition mutation, False otherwise.
        """

        return (nucleotide1, nucleotide2) in [("A", "G"), ("G", "A"), ("C", "T"), ("T", "C")]
