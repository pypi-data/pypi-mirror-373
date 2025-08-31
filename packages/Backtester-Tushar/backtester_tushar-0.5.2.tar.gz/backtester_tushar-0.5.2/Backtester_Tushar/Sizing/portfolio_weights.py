
def select_optimal_portfolio(signals_df, n_long_positions, k_short_positions,):
    """Select optimal portfolio using advanced signal processing"""
    if len(signals_df) == 0:
        return {}, {}

    long_portfolio = _select_long_portfolio(signals_df, n_long_positions)
    short_portfolio = _select_short_portfolio(signals_df, k_short_positions)

    return long_portfolio, short_portfolio

def _select_long_portfolio(signals_df, n_long_positions):
    """Select optimal long portfolio"""
    if len(signals_df) == 0:
        return {}

    # Filter for positive signals
    long_signals = signals_df[signals_df['signal_descriptor'] > 0].copy()
    if len(long_signals) == 0:
        return {}

    long_signals_sorted = long_signals.nlargest(
        min(n_long_positions * 2, len(long_signals)), 'signal_descriptor'
    )
    scores = []
    tickers = []
    for _, row in long_signals_sorted.iterrows():
        atr = row.get('ATR', None)
        close = row['Close']
        if atr is None:
            atr_pct = 0.02
        else:
            atr_pct = atr / close
        base_score = row['signal_descriptor'] / (1 + max(atr_pct, 0.02))
        adjusted_score = base_score
        scores.append(adjusted_score)
        tickers.append(row['ticker'])
    selected_ticker = tickers[:n_long_positions]
    selected_scores = scores[:n_long_positions]
    weights = [score / sum(selected_scores) for score in selected_scores]

    portfolio = {}
    for i in range(len(weights)):
        portfolio[selected_ticker[i]] = weights[i]
    return portfolio

def _select_short_portfolio(signals_df, k_short_positions):
    """Select optimal short portfolio"""
    if len(signals_df) == 0:
        return {}

    # Filter for negative signals
    short_signals = signals_df[signals_df['signal_descriptor'] < 0].copy()
    if len(short_signals) == 0:
        return {}

    short_signals_sorted = short_signals.nsmallest(
        min(k_short_positions * 2, len(short_signals)), 'signal_descriptor'
    )

    scores = []
    tickers = []
    for _, row in short_signals_sorted.iterrows():
        atr = row.get('ATR', None)
        close = row['Close']
        if atr is None:
            atr_pct = 0.02
        else:
            atr_pct = atr / close
        base_score = row['signal_descriptor'] / (1 + max(atr_pct, 0.02))
        adjusted_score = base_score
        scores.append(adjusted_score)
        tickers.append(row['ticker'])
    selected_ticker = tickers[:k_short_positions]
    selected_scores = scores[:k_short_positions]
    weights = [score / sum(selected_scores) for score in selected_scores]

    portfolio = {}
    for i in range(len(weights)):
        portfolio[selected_ticker[i]] = weights[i]
    return portfolio