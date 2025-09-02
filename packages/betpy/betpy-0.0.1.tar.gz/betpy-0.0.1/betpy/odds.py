import numpy as np
import pandas as pd


class Probability():
    def __init__(self, p):
        self.p = p 

    @property
    def a(self):
        # if self.d <= 2:
        #     odds = -100 / (self.d - 1)
        # else:
        #     odds = 100 * (self.d - 1)
        odds = np.where(self.d <= 2,
                        -100 / (self.d - 1),
                        100 * (self.d - 1))
        return (np.round(odds)).astype(int)

    @property
    def f(self):
        return self.d - 1

    @property
    def d(self):
        return 1 / self.p



class Odds(Probability):
    def __init__(self, odds, otype='american'):
        # otype in ['american', 'decimal', 'fractional']
        if otype == 'american':
            if isinstance(odds, str):
                odds = int(odds)
            # Convert to decimal odds
            d_odds = np.where(odds < 0, 
                              1 + 100 / -odds,
                              1 + odds / 100)
            # if odds < 0:
            #     d_odds = 1 + 100 / -odds
            # else:
            #     d_odds = 1 + odds / 100
        elif otype == 'fractional':
            d_odds = 1 + odds
        elif otype == 'decimal':
            d_odds = odds
        self.p = 1. / d_odds

    




