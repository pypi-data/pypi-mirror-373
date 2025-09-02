from . import odds as _odds


# def kelly(win_prob, im_prob):
#     if isinstance(win_prob, _odds.Odds):
#         win_prob = win_prob.p
#     if isinstance(im_prob, _odds.Odds):
#         d_odds = im_prob.d
#     else:
#         d_odds = _odds.im_odds(im_prob, otype='D')
#     return win_prob - (1 - win_prob) / (d_odds - 1)


def kelly_criterion(true_prob, im_prob):
    """
    Kelly Criterion calculation with Probability objects (such as Odds).

    Should extend this to accept any format (but consistent between the two).
    """
    return true_prob.p - (1 - true_prob.p) / (im_prob.d - 1)