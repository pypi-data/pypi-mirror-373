import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def brier_score(score, prob):
    return 1 / len(score) * (score - prob)**2


class EloEngine():
    # Ref: https://elo.jprmesh.xyz/
    # http://www.glicko.net/glicko/glicko2.pdf
    def __init__(self, df, starting=1500, K=30, c=400):
        """
        df: dataframe with input data
        """
        self.history_df = df.copy()
        self.starting = starting
        self.K = K
        self.c = c

        self.teams = np.union1d(self.history_df['Team1'].unique(), 
                                self.history_df['Team2'].unique())

        self.elo_dict = {team: [self.starting] for team in self.teams}

        self.run()

    @property
    def elo_ranking(self):
        return sorted([(k, v[-1]) for k, v in self.elo_dict.items()],
                      key=lambda x: x[1], reverse=True)

    @property
    def brier_score(self):
        """
        Since S1 - P1 = -(S2 - P2), doesn't matter which team we use for this calculation.
        """
        return np.mean((self.history_df['Team1EloScore'] - self.history_df['Team1Prob'])**2)

    def get_elo(self, team):
        return self.elo_dict[team][-1]

    def win_prob(self, elo1, elo2):
        return 1 / (np.power(10, -(elo1 - elo2) / self.c) + 1)

    def team_win_prob(self, team1, team2):
        return self.win_prob(self.get_elo(team1),
                             self.get_elo(team2))

    def get_M(self, W, L):
        return (W * (W - L) / (W + L))**0.7

    def run(self):
        self.elo_dict = {team: [self.starting] for team in self.teams}
        for i, game in self.history_df.iterrows():
            elo1 = self.elo_dict[game['Team1']][-1]
            elo2 = self.elo_dict[game['Team2']][-1]
            P1 = self.win_prob(elo1, elo2)
            P2 = 1 - P1
            self.history_df.loc[i, 'Team1Prob'] = P1
            self.history_df.loc[i, 'Team2Prob'] = P2
            S1 = game['Team1EloScore']
            S2 = game['Team2EloScore']

            M = 1
            adj1 = self.K * M * (S1 - P1)
            # This should just be -adj1
            adj2 = self.K * M * (S2 - P2)

            self.elo_dict[game['Team1']].append(elo1 + adj1)
            self.elo_dict[game['Team2']].append(elo2 + adj2)

    def plot(self):
        for team in self.teams:
            plt.plot(self.elo_dict[team], lw=2, label=team)
        plt.legend()
