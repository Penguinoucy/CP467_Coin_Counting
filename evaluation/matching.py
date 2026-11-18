"""Role 4 implements the matching rule from the proposal."""
def match_coins(predicted_coins, labelled_coins):
    """Return [(prediction_index, label_index), ...].
    Allow a match only when centre distance <= 0.5 * labelled radius.
    Maximize match count, then minimize total centre distance among ties.
    No prediction or label may be used more than once. Do not use greedy matching.
    """
    raise NotImplementedError("Role 4 must implement evaluation/matching.py")
