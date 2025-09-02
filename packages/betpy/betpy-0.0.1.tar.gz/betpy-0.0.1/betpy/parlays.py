import numpy as np
from . import odds as _odds


def parlay_odds(odds, otype_in='A', otype_out='A'):
    """
    Combine parlay odds, presented as a list.
    """
    prob = _odds.im_prob(odds, otype=otype_in)
    parlay_prob = np.prod(prob)
    return _odds.im_odds(parlay_prob, otype=otype_out)
