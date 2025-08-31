min_coding_region_length = 7 * 3  # start_codon_length + stop_codon_length + 5 codons length in the coding area


class DNAUtils:
    @staticmethod
    def find_overlapping_regions(dna_sequence):
        start_codon = 'ATG'
        stop_codons = {'TAA', 'TAG', 'TGA'}
        coding_regions = []
        sequence_length = len(dna_sequence)

        # Check all three reading frames
        for frame in range(3):
            i = frame
            while i < sequence_length - 2:
                if dna_sequence[i:i + 3] == start_codon:
                    # Found a start codon, now look for a stop codon
                    for j in range(i + 3, sequence_length - 2, 3):
                        if dna_sequence[j:j + 3] in stop_codons:
                            if len(dna_sequence[i:j + 3]) > min_coding_region_length:
                                coding_regions.append((i, j + 2))
                                i = j + 3  # Move to the next possible start codon
                                break
                i += 3  # Move to the next codon in this reading frame

        overlaps = []

        # Compare each pair of coding regions for overlap
        for i, (start1, end1) in enumerate(coding_regions):
            for j, (start2, end2) in enumerate(coding_regions):
                if i < j:  # Ensure we only check each pair once
                    # Check if the regions overlap
                    if (start1 <= start2 <= end1) or (start2 <= start1 <= end2):
                        overlaps.append(((start1 + 1, end1 + 1), (start2 + 1, end2 + 1)))

        return len(overlaps) > 0, overlaps

    @staticmethod
    def get_overlapping_regions(dna_sequence, overlaps, flank=10):
        info = f"Target Sequence Length: {len(dna_sequence)}\n"

        for (start1, end1), (start2, end2) in overlaps:
            # Convert to 0-based indexing
            start1 -= 1
            end1 -= 1
            start2 -= 1
            end2 -= 1

            overlap_start = max(start1, start2)
            overlap_end = min(end1, end2)

            if overlap_start > overlap_end:
                continue  # No real overlap, skip

            overlap_region = dna_sequence[overlap_start:overlap_end + 1]
            overlap_len = len(overlap_region)

            # Extract context
            left_flank = max(0, overlap_start - flank)
            right_flank = min(len(dna_sequence), overlap_end + flank + 1)

            context_seq = dna_sequence[left_flank:right_flank]
            pointer_line = (
                    " " * (overlap_start - left_flank)
                    + "^" * overlap_len
            )

            info += (
                f"\nOverlap between ORFs ({start1 + 1}–{end1 + 1}) and ({start2 + 1}–{end2 + 1})\n"
                f"Shared Region:   {overlap_region}\n"
                f"                 ↑ overlap of {overlap_len} bp at positions {overlap_start + 1}–{overlap_end + 1}\n"
                f"\nContext:\n"
                f"{context_seq}\n"
                f"{pointer_line}\n"
            )

        return info

    @staticmethod
    def get_coding_regions_list(coding_indexes, seq):
        """
        Constructs a dictionary of coding regions from coding index ranges.

        Parameters:
            coding_indexes (list of tuples): List of (start, end) tuples representing coding regions.
            seq (str): The full DNA sequence.

        Returns:
            dict: A dictionary where keys are coding region numbers (as strings) and values are the corresponding sequences.
        """
        coding_regions_list = {}

        for region_counter, (start, end) in enumerate(coding_indexes, start=1):
            # Extract the sequence for the current coding region
            coding_regions_list[str(region_counter)] = seq[start:end]

        return coding_regions_list

    @staticmethod
    def get_coding_and_non_coding_regions_positions(seq):
        """
        Identifies coding regions in the DNA sequence and precomputes an array of codon positions.

        Args:
            seq (str): The DNA sequence to analyze.
        Returns:
            tuple: (codon_positions, coding_region_indexes)
                - codon_positions: list of codon positions per base (0, 1, 2, 3, or -3)
                - coding_region_indexes: list of tuples indicating start and end of each coding region
        """
        start_codon = "ATG"
        stop_codons = {"TAA", "TAG", "TGA"}

        N = len(seq)
        codon_positions = [0] * N  # Initialize all positions as non-coding (0)
        coding_region_indexes = []

        i = 0  # Pointer to traverse the sequence

        while i < len(seq) - 2:
            if seq[i:i + 3] == start_codon:
                # Search for the nearest stop codon in the same reading frame
                for j in range(i + 3, len(seq) - 2, 3):
                    if seq[j:j + 3] in stop_codons:
                        start_idx = i
                        end_idx = j + 3  # Include the stop codon

                        if end_idx - start_idx >= min_coding_region_length:
                            for k in range(start_idx, end_idx):
                                codon_phase = ((k - start_idx) % 3) + 1
                                if (k - start_idx) < 3 and codon_phase == 3:
                                    # Only mark the third position of the **first start codon**
                                    codon_positions[k] = -3
                                else:
                                    codon_positions[k] = codon_phase

                            coding_region_indexes.append((start_idx, end_idx))
                        i = end_idx  # Move the pointer past the coding region
                        break
                else:
                    # No valid stop codon found in frame, treat rest as non-coding
                    break
            else:
                i += 1

        return codon_positions, coding_region_indexes
