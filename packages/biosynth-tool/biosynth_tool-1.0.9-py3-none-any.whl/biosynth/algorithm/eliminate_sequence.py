from collections import defaultdict

from biosynth.algorithm.fsm import FSM
from biosynth.data.app_data import CostData
from biosynth.utils.info_utils import format_cost, get_elimination_process_description, \
    get_non_coding_region_cost_description, get_coding_region_cost_description
from biosynth.utils.cost_utils import EliminationScorerConfig
from biosynth.utils.date_utils import format_current_date
from biosynth.utils.text_utils import format_text_bold_for_output


class EliminationController:
    @staticmethod
    def eliminate(target_sequence, unwanted_patterns, coding_positions):
        # Initialize information string for the elimination process
        info = f"{format_text_bold_for_output('Target Sequence:')}\n{target_sequence}\n"
        info += f"\n{format_text_bold_for_output('Unwanted Patterns:')}\n{', '.join(sorted(unwanted_patterns))}\n"

        # Check if unwanted patterns exist
        if not any(x in target_sequence for x in unwanted_patterns):
            info += "\nNo invalid patterns identified — the original sequence will be retained."
            return info, None, target_sequence, 0.0  # Return unchanged sequence

        # Additional descriptions (placeholders for actual descriptions)
        info += f"\n{format_text_bold_for_output(get_elimination_process_description())}\n"
        info += f"\nNon-Coding regions:\n{get_non_coding_region_cost_description()}\n"
        info += f"\nCoding regions:\n{get_coding_region_cost_description()}\n"

        n = len(target_sequence)

        # Initialize utility and FSM classes
        elimination_scorer = EliminationScorerConfig()
        initial_cost_function, cost_function = elimination_scorer.cost_function(target_sequence,
                                                                                coding_positions,
                                                                                CostData.codon_usage,
                                                                                CostData.alpha,
                                                                                CostData.beta,
                                                                                CostData.w)
        fsm = FSM(unwanted_patterns, elimination_scorer.alphabet)

        # Dynamic programming table A, initialized with infinity
        A = defaultdict(lambda: float('inf'))
        # A* table for backtracking (stores the previous state and transition symbol)
        A_star = {}
        A_info = {}

        # Initialize all bigram states in column 2
        for v in fsm.V:
            if len(v) == 2:
                changes_1, cost_f_1 = initial_cost_function(1, v[0])
                changes_2, cost_f_2 = initial_cost_function(2, v[1])

                cost = cost_f_1 + cost_f_2
                changes = changes_1[0] + changes_2[0], changes_1[1] + changes_2[1]

                A[(2, v)] = cost
                A_info[(2, v)] = changes, cost

        # Fill the dynamic programming table
        for i in range(3, n + 1):
            for v in fsm.V:
                best_cost = float('inf')
                best_prev = None
                best_info = None
                for u in fsm.V:
                    for sigma in fsm.sigma:
                        if fsm.f.get((u, sigma)) == v:
                            changes, cost_f = cost_function(i, u, sigma)
                            cost = A[(i - 1, u)] + cost_f
                            if cost < best_cost:
                                best_cost = cost
                                best_prev = (u, sigma)
                                best_info = (changes, cost_f)

                if best_prev is not None:
                    A[(i, v)] = best_cost
                    A_star[(i, v)] = best_prev
                    A_info[(i, v)] = best_info

        # Find the minimum cost and final state
        min_cost = float('inf')
        final_state = None
        for v in fsm.V:
            if A[(n, v)] < min_cost:
                min_cost = A[(n, v)]
                final_state = v

        # If no valid sequence was found
        if min_cost == float('inf'):
            info += "\nNo valid sequence found that avoids the unwanted patterns."
            return info, None, None, min_cost

        # Reconstruct the sequence with the minimum cost
        path = []
        sequence = []
        changes_info = []

        # starting from the end
        current_state = final_state

        # Backtrack to reconstruct the sequence
        for i in range(n, 2, -1):
            if (i, current_state) not in A_star:
                raise ValueError(f"No transition found for position {i} and state {current_state}")

            prev_state, char = A_star[(i, current_state)]  # Get the previous state and symbol
            changes, cost_f = A_info[(i, current_state)]

            # Record the change that actually occurred
            if cost_f > 0.0:
                changes_info.append(
                    f"Position {str(i).ljust(6)}  {changes[0].ljust(6)} ->   {changes[1].ljust(6)}   Cost: {cost_f:.2f}"
                )

            path.append((i, current_state))
            sequence.append(char)

            current_state = prev_state

        # Concatenate S after v2
        path.append((2, current_state))
        sequence.append(current_state)

        # Reconstruct the first two positions (0 and 1) from current_state
        # Check and log changes at positions 0 and 1
        original_0, original_1 = target_sequence[0], target_sequence[1]

        if coding_positions[1] == 0:
            if current_state[1] != original_1:
                changes, cost_f = initial_cost_function(2, current_state[1])
                changes_info.append(
                    f"Position {str(2).ljust(6)}  {changes[0].ljust(6)} ->   {changes[1].ljust(6)}   Cost: {cost_f:.2f}"
                )

        if coding_positions[0] == 0:
            if current_state[0] != original_0:
                changes, cost_f = initial_cost_function(1, current_state[0])
                changes_info.append(
                    f"Position {str(1).ljust(6)}  {changes[0].ljust(6)} ->   {changes[1].ljust(6)}   Cost: {cost_f:.2f}"
                )

        # Reverse the sequence and changes info for correct order
        path.reverse()
        sequence.reverse()
        changes_info.reverse()

        # Append final information to the info string
        info += f"\n{format_text_bold_for_output('_' * 50)}\n"
        info += "\n🚀 Elimination Process Completed!\n"
        info += f"📆 {format_current_date()}"

        return info, changes_info, ''.join(sequence), min_cost
