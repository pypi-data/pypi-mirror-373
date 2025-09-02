import pandas as pd 
from sklearn.base import BaseEstimator, TransformerMixin
import betpy.odds as _odds

# --- Strategy Component 1: Bet Sizing (e.g., Kelly Criterion) ---
def calculate_kelly_criterion(model_prob, odds):
    """Calculates the fraction of capital to bet."""
    b = odds - 1  # Decimal odds to fractional odds
    p = model_prob
    q = 1 - p
    
    # Kelly formula
    fraction = (b * p - q) / b
    
    # Bet nothing if edge is not positive
    fraction[fraction < 0] = 0
    return fraction

class OneSidedStrategyWrapper(BaseEstimator, TransformerMixin):
    def __init__(self, model_pipeline, feature_cols, odds_col, decision_threshold=0.0, sizing_strategy='kelly'):
        self.model_pipeline = model_pipeline
        self.feature_cols = feature_cols
        self.odds_col = odds_col
        self.decision_threshold = decision_threshold
        self.sizing_strategy = sizing_strategy

    def fit(self, X, y=None):
        # We only need to fit the internal model pipeline
        X_features = X[self.feature_cols]
        print(f"Fitting model pipeline on features: {X_features.columns.tolist()}")
        self.model_pipeline.fit(X_features, y)
        return self

    def transform(self, X):
        # Separate features and side info from the input DataFrame
        X_features = X[self.feature_cols]
        odds = X[self.odds_col]

        # Get predictions from the fitted internal model
        # We assume binary classification and want the probability of the positive class (1)
        model_probs = self.model_pipeline.predict_proba(X_features)[:, 1]

        # Apply the decision rule
        # Bet if our model's probability exceeds the implied probability by a threshold
        implied_prob = _odds.Odds(odds).p
        bet_signal = (model_probs - implied_prob) >= self.decision_threshold

        # Apply the sizing strategy
        if self.sizing_strategy == 'kelly':
            bet_size = calculate_kelly_criterion(model_probs, odds)
        elif self.sizing_strategy == 'fixed':
            bet_size = 1.0  # Bet a fixed unit size
        else:
            bet_size = 0.0

        # Combine signal and size (only size the bets we decide to make)
        final_bet_size = bet_size * bet_signal
        
        # Return a clean, structured DataFrame as the output
        results = pd.DataFrame({
            'model_prob': model_probs,
            'implied_prob': implied_prob,
            'bet_signal': bet_signal,
            'bet_size': final_bet_size
        }, index=X.index)
        
        return results