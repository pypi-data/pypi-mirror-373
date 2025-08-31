from collections import deque


def kmp_based_fsm_bigram(unwanted_patterns, sigma):
    """
    Constructs the FSM by calculating the states and transition function.

    Args:
        unwanted_patterns (set): The set of unwanted patterns.
        sigma (set): The alphabet of allowed characters.

    Returns:
        V (set): The set of states in the FSM.
        f (dict): The transition function of the FSM, mapping (state, character) pairs to new states.
        g (dict): A helper function used to compute the transition function.
    """

    f = {}
    g = {}
    states = set()
    epsilon = ''

    # Prefix elongation and invalid transitions
    for p in unwanted_patterns:
        for j in range(1, len(p) + 1):
            f[(p[:j - 1], p[j - 1])] = p[:j]
        f[(p[:- 1], p[- 1])] = None  # Invalid transition into complete pattern

    # Computing state space V and the functions f and g
    state_queue = deque()
    states.add(epsilon)
    for s in sigma:
        if (epsilon, s) not in f:
            f[(epsilon, s)] = epsilon
        if f[(epsilon, s)] == s:
            g[s] = epsilon
            state_queue.append(s)

    # Efficient BFS State Processing in FSM Pattern Matching
    while state_queue:
        v = state_queue.popleft()
        states.add(v)

        for s in sigma:
            if f[g[v], s] is None:
                f[(v, s)] = None
            if (v, s) not in f:
                f[(v, s)] = f[(g[v], s)]
            if f[(v, s)] == v + s:
                g[v + s] = f[(g[v], s)]
                state_queue.append(v + s)

    # Remove epsilon and single-character states
    states.remove(epsilon)
    for s in sigma:
        if s in states:
            states.remove(s)

    # Remove transitions of invalid_states
    for (v, s) in f.copy():
        if v in sigma | {epsilon}:
            del f[(v, s)]

    # Generate all bigrams from the alphabet and update states
    for x in sigma:
        for y in sigma:
            states.add(x + y)

    # Clean and fix transitions in a single pass
    for v in states:
        for s in sigma:
            if (v, s) not in f or f[(v, s)] in sigma | {epsilon}:
                f[(v, s)] = v[-1] + s

    return states, f, g


class FSM:
    """
    A class representing a finite state machine (FSM) for eliminating unwanted patterns from a sequence.

    Attributes:
        sigma (set): The alphabet of allowed characters in the sequence.
        unwanted_patterns (set): The set of unwanted patterns to be eliminated.
        V (set): The set of states in the FSM.
        f (dict): The transition function of the FSM, mapping (state, character) pairs to new states.
        g (dict): A helper function used to compute the transition function.

    Methods:
        __init__(self, unwanted_patterns, alphabet): Initializes the FSM with the given unwanted patterns and alphabet.
        calculate_fsm(self, P, Σ): Constructs the FSM by calculating the states and transition function.
    """

    def __init__(self, unwanted_patterns, alphabet):
        """
        Initializes the FSM with the given unwanted patterns and alphabet.

        Args:
            unwanted_patterns (set): The set of unwanted patterns to be eliminated.
            alphabet (set): The alphabet of allowed characters in the sequence.
        """
        self.sigma = alphabet
        self.unwanted_patterns = unwanted_patterns

        self.V, self.f, self.g = kmp_based_fsm_bigram(self.unwanted_patterns, self.sigma)
