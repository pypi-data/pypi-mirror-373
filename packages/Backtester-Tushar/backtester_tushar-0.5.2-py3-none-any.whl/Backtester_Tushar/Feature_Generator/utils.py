import pandas as pd
import numpy as np
import os
import warnings
from astropy.timeseries import LombScargle
from scipy.spatial import KDTree
from arch import arch_model


def _compute_rsi(series, period=14):
    """
    Compute the Relative Strength Index (RSI).

    The RSI is a momentum oscillator based on average gains and losses over a rolling window.

    Formula
    -------
    RS  = (avg_gain over N) / (avg_loss over N)
    RSI = 100 - (100 / (1 + RS))

    Parameters
    ----------
    series : pd.Series
        Price series (typically closing prices), indexed by time.
    period : int, default=14
        Lookback window length.

    Returns
    -------
    pd.Series
        RSI values aligned to `series.index`.

    Value Range
    -----------
    [0, 100]
      • >70 often considered overbought
      • <30 often considered oversold

    Notes
    -----
    - Uses simple rolling means (not Wilder’s smoothing).
    - First `period` observations return NaN due to insufficient lookback.
    """
    delta = series.diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain, index=series.index).rolling(period).mean()
    avg_loss = pd.Series(loss, index=series.index).rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def _compute_bollinger(series, period=20, num_std=2):
    """
    Compute Bollinger Bands (upper and lower).

    Formula
    -------
    MA    = SMA(period)
    Upper = MA + num_std * StdDev(period)
    Lower = MA - num_std * StdDev(period)

    Parameters
    ----------
    series : pd.Series
        Price series (e.g., close).
    period : int, default=20
        Rolling window for mean and standard deviation.
    num_std : float, default=2
        Standard deviation multiplier.

    Returns
    -------
    pd.DataFrame
        Two-column DataFrame: [UpperBand, LowerBand], indexed like `series`.

    Value Range
    -----------
    Unbounded; same price scale as `series`.

    Notes
    -----
    - Wider bands imply higher realized volatility.
    - Output columns are unnamed; you may rename as needed after calling.
    """
    ma = series.rolling(period).mean()
    std = series.rolling(period).std()
    upper = ma + num_std * std
    lower = ma - num_std * std
    return pd.concat([upper, lower], axis=1)


def _compute_bollinger_width(series, period=20, num_std=2):
    """
    Compute Bollinger Band width as a fraction of the moving average.

    Formula
    -------
    Width = (Upper - Lower) / SMA(period)

    Parameters
    ----------
    series : pd.Series
        Price series.
    period : int, default=20
        Rolling window.
    num_std : float, default=2
        Standard deviation multiplier.

    Returns
    -------
    pd.Series
        Relative band width.

    Value Range
    -----------
    [0, +∞)
      • 0 when std = 0 (flat price)
      • No fixed upper bound

    Notes
    -----
    - Spikes often coincide with volatility expansions.
    """
    upper, lower = _compute_bollinger(series, period, num_std).T.values
    return (upper - lower) / series.rolling(period).mean()


def _compute_bollinger_position(series, period=20, num_std=2):
    """
    Compute normalized price position within Bollinger Bands.

    Formula
    -------
    Pos = (Price - Lower) / (Upper - Lower)

    Parameters
    ----------
    series : pd.Series
        Price series.
    period : int, default=20
        Rolling window.
    num_std : float, default=2
        Standard deviation multiplier.

    Returns
    -------
    pd.Series
        Position metric.

    Value Range
    -----------
    Typically [0, 1]
      • 0 at lower band
      • 1 at upper band
      • Can be <0 or >1 if price pierces bands

    Notes
    -----
    - Returns NaN when (Upper - Lower) == 0 (e.g., flat market).
    """
    upper, lower = _compute_bollinger(series, period, num_std).T.values
    return (series - lower) / (upper - lower)


def _compute_macd(series, fast=12, slow=26, signal=9):
    """
    Compute MACD, Signal line, and Histogram.

    Formula
    -------
    MACD      = EMA(fast) - EMA(slow)
    MACD_Sig  = EMA(MACD, signal)
    MACD_Hist = MACD - MACD_Sig

    Parameters
    ----------
    series : pd.Series
        Price series.
    fast : int, default=12
        Fast EMA span.
    slow : int, default=26
        Slow EMA span.
    signal : int, default=9
        Signal EMA span.

    Returns
    -------
    pd.DataFrame
        Columns: {"MACD", "MACD_Signal", "MACD_Hist"}.

    Value Range
    -----------
    Unbounded; scale proportional to `series`.

    Notes
    -----
    - Positive histogram indicates bullish momentum vs. signal line.
    """
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    macd_signal = macd.ewm(span=signal, adjust=False).mean()
    macd_hist = macd - macd_signal
    return pd.DataFrame({"MACD": macd, "MACD_Signal": macd_signal, "MACD_Hist": macd_hist})


def _compute_atr(df, period=14):
    """
    Compute the Average True Range (ATR) as a volatility measure.

    Formula
    -------
    TR_t = max(High_t - Low_t, |High_t - Close_{t-1}|, |Low_t - Close_{t-1}|)
    ATR  = SMA(TR, period)

    Parameters
    ----------
    df : pd.DataFrame
        Must contain ["High", "Low", "Close"].
    period : int, default=14
        Rolling window for average true range.

    Returns
    -------
    pd.Series
        ATR values indexed like `df`.

    Value Range
    -----------
    [0, +∞)
      • Same price units as input.

    Notes
    -----
    - Higher ATR implies higher realized volatility.
    """
    high_low = df["High"] - df["Low"]
    high_close = np.abs(df["High"] - df["Close"].shift())
    low_close = np.abs(df["Low"] - df["Close"].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    return atr


def _compute_adx(df, period=14):
    """
    Compute the Average Directional Index (ADX) for trend strength.

    Implementation Notes
    --------------------
    This implementation follows the classical +DM / -DM and TR relationships,
    then derives +DI and -DI, and finally the DX and ADX.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain ["High", "Low", "Close"].
    period : int, default=14
        Lookback window.

    Returns
    -------
    pd.Series
        ADX values.

    Value Range
    -----------
    [0, 100]
      • >25 often interpreted as a strong trend

    Caveats
    -------
    - Early values are NaN due to rolling windows.
    - Different ADX formulations exist (e.g., Wilder smoothing).
    """
    plus_dm = df["High"].diff()
    minus_dm = df["Low"].diff().abs()
    plus_dm = np.where((plus_dm > minus_dm) & (plus_dm > 0), plus_dm, 0)
    minus_dm = np.where((minus_dm > plus_dm) & (minus_dm > 0), minus_dm, 0)
    tr = _compute_atr(df, period)
    plus_di = 100 * (pd.Series(plus_dm, index=df.index).rolling(period).sum() / tr)
    minus_di = 100 * (pd.Series(minus_dm, index=df.index).rolling(period).sum() / tr)
    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    adx = dx.rolling(period).mean()
    return adx


def _compute_cci(df, period=20):
    """
    Compute the Commodity Channel Index (CCI).

    Formula
    -------
    TP  = (High + Low + Close) / 3
    SMA = SMA(TP, period)
    MD  = SMA(|TP - SMA|, period)
    CCI = (TP - SMA) / (0.015 * MD)

    Parameters
    ----------
    df : pd.DataFrame
        Must contain ["High", "Low", "Close"].
    period : int, default=20
        Rolling window.

    Returns
    -------
    pd.Series
        CCI values.

    Value Range
    -----------
    Unbounded
      • ±100/±200 are common thresholds in practice

    Notes
    -----
    - Larger absolute values indicate larger deviations from the rolling mean.
    """
    tp = (df["High"] + df["Low"] + df["Close"]) / 3
    ma = tp.rolling(period).mean()
    md = (tp - ma).abs().rolling(period).mean()
    cci = (tp - ma) / (0.015 * md)
    return cci


def _compute_stochastic(df, k_period=14, d_period=3):
    """
    Compute Stochastic Oscillator %K and %D.

    Formula
    -------
    %K = 100 * (Close - LowestLow_{k}) / (HighestHigh_{k} - LowestLow_{k})
    %D = SMA(%K, d_period)

    Parameters
    ----------
    df : pd.DataFrame
        Must contain ["High", "Low", "Close"].
    k_period : int, default=14
        Lookback for %K.
    d_period : int, default=3
        SMA lookback for %D.

    Returns
    -------
    tuple[pd.Series, pd.Series]
        (%K, %D) series.

    Value Range
    -----------
    %K: [0, 100] (may be NaN when denominator is 0)
    %D: [0, 100] (moving average of %K)

    Notes
    -----
    - When HighestHigh == LowestLow, %K is undefined (NaN).
    """
    low_min = df["Low"].rolling(k_period).min()
    high_max = df["High"].rolling(k_period).max()
    k = 100 * (df["Close"] - low_min) / (high_max - low_min)
    d = k.rolling(d_period).mean()
    return k, d


def _compute_williams_r(df, period=14):
    """
    Compute Williams %R, a momentum oscillator.

    Formula
    -------
    %R = -100 * (HighestHigh_{N} - Close) / (HighestHigh_{N} - LowestLow_{N})

    Parameters
    ----------
    df : pd.DataFrame
        Must contain ["High", "Low", "Close"].
    period : int, default=14
        Lookback window.

    Returns
    -------
    pd.Series
        Williams %R values.

    Value Range
    -----------
    [-100, 0] (NaN if denominator is 0)
      • Near 0   → overbought
      • Near -100 → oversold
    """
    high_max = df["High"].rolling(period).max()
    low_min = df["Low"].rolling(period).min()
    wr = -100 * (high_max - df["Close"]) / (high_max - low_min)
    return wr


def _compute_obv(df):
    """
    Compute On-Balance Volume (OBV).

    OBV cumulates volume with the sign of daily price changes.

    Algorithm
    ---------
    direction_t = sign(Close_t - Close_{t-1})
    OBV_t = OBV_{t-1} + direction_t * Volume_t

    Parameters
    ----------
    df : pd.DataFrame
        Must contain ["Close", "Volume"].

    Returns
    -------
    pd.Series
        OBV series (cumulative).

    Value Range
    -----------
    Unbounded; scale depends on cumulative volumes and trend direction.

    Notes
    -----
    - Flat price changes (delta = 0) contribute 0 to OBV.
    """
    direction = np.sign(df["Close"].diff()).fillna(0)
    obv = (direction * df["Volume"]).cumsum()
    return obv


def _compute_cmf(df, period=20):
    """
    Compute Chaikin Money Flow (CMF).

    Formula
    -------
    MFM_t = ((Close - Low) - (High - Close)) / (High - Low)   # Money Flow Multiplier
    MFV_t = MFM_t * Volume                                    # Money Flow Volume
    CMF   = sum(MFV over N) / sum(Volume over N)

    Parameters
    ----------
    df : pd.DataFrame
        Must contain ["High", "Low", "Close", "Volume"].
    period : int, default=20
        Rolling window for sums.

    Returns
    -------
    pd.Series
        CMF values.

    Value Range
    -----------
    Typically in [-1, 1]
      • Can exceed slightly outside due to edge cases (e.g., division precision)

    Notes
    -----
    - When High == Low, MFM is undefined; this implementation yields NaN for that bar.
    """
    mfm = ((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / (df["High"] - df["Low"])
    mfv = mfm * df["Volume"]
    cmf = mfv.rolling(period).sum() / df["Volume"].rolling(period).sum()
    return cmf


def _compute_mfi(df, period=14):
    """
    Compute Money Flow Index (MFI), a volume-weighted momentum oscillator.

    Formula
    -------
    TP_t  = (High + Low + Close) / 3                # Typical Price
    MF_t  = TP_t * Volume_t                         # Raw Money Flow
    +MF_t = MF_t if TP_t > TP_{t-1} else 0
    -MF_t = MF_t if TP_t < TP_{t-1} else 0
    MFR   = sum(+MF over N) / sum(-MF over N)       # Money Flow Ratio
    MFI   = 100 - 100 / (1 + MFR)

    Parameters
    ----------
    df : pd.DataFrame
        Must contain ["High", "Low", "Close", "Volume"].
    period : int, default=14
        Rolling window.

    Returns
    -------
    pd.Series
        MFI values.

    Value Range
    -----------
    [0, 100]
      • >80 often considered overbought
      • <20 often considered oversold

    Notes
    -----
    - If sum(-MF) == 0 in the window, MFR → ∞ and MFI → 100.
    - If sum(+MF) == 0, MFR → 0 and MFI → 0.
    """
    tp = (df["High"] + df["Low"] + df["Close"]) / 3
    mf = tp * df["Volume"]
    pos_mf = np.where(tp > tp.shift(), mf, 0)
    neg_mf = np.where(tp < tp.shift(), mf, 0)
    pos_sum = pd.Series(pos_mf, index=df.index).rolling(period).sum()
    neg_sum = pd.Series(neg_mf, index=df.index).rolling(period).sum()
    mfr = pos_sum / neg_sum
    mfi = 100 - (100 / (1 + mfr))
    return mfi


def _compute_vwap(df):
    """
    Compute Volume-Weighted Average Price (VWAP) cumulatively from the start of the series.

    Formula
    -------
    TP_t   = (High + Low + Close) / 3
    VWAP_t = cumsum(Volume * TP) / cumsum(Volume)

    Parameters
    ----------
    df : pd.DataFrame
        Must contain ["High", "Low", "Close", "Volume"].

    Returns
    -------
    pd.Series
        Cumulative VWAP.

    Value Range
    -----------
    Unbounded; same price scale as input.

    Notes
    -----
    - This is a running (from inception) VWAP, not a session/day-reset VWAP.
    """
    return (df["Volume"] * (df["High"] + df["Low"] + df["Close"]) / 3).cumsum() / df["Volume"].cumsum()


def _compute_volatility_regime(df, period=20):
    """
    Compute a continuous volatility regime score via ATR percentile.

    Method
    ------
    vol_score = rank_pct(ATR(period))

    Parameters
    ----------
    df : pd.DataFrame
        Must contain ["High", "Low", "Close"].
    period : int, default=20
        ATR lookback.

    Returns
    -------
    pd.Series
        Volatility score per bar.

    Value Range
    -----------
    [0.0, 1.0]
      • 0.0 = lowest ATR in sample
      • 1.0 = highest ATR in sample

    Notes
    -----
    - Percentile is computed across the entire series (not rolling).
    """
    atr = _compute_atr(df, period)
    vol_score = atr.rank(pct=True)
    return vol_score


def _compute_trend_regime(df, ma_period=50, adx_period=14):
    """
    Compute a continuous trend regime score using MA slope sign and normalized ADX.

    Method
    ------
    MA      = SMA(Close, ma_period)
    slope   = sign(diff(MA))
    strength= ADX(adx_period) / 100
    score   = slope * strength

    Parameters
    ----------
    df : pd.DataFrame
        Must contain ["Close", "High", "Low"] (ADX uses H/L/C).
    ma_period : int, default=50
        Moving average length to estimate direction.
    adx_period : int, default=14
        ADX lookback for trend strength.

    Returns
    -------
    pd.Series
        Trend regime score.

    Value Range
    -----------
    [-1.0, 1.0]
      • Negative = downtrend (strength-weighted)
      • Positive = uptrend (strength-weighted)
      • Magnitude increases with ADX

    Notes
    -----
    - Returns 0 when ADX is zero or MA slope is flat.
    """
    ma = df["Close"].rolling(ma_period).mean()
    slope = ma.diff()
    adx = _compute_adx(df, period=adx_period)
    adx_norm = adx / 100.0
    slope_sign = np.sign(slope)
    trend_score = adx_norm * slope_sign
    return pd.Series(trend_score, index=df.index).fillna(0)


def _compute_liquidity_regime(df, period=20):
    """
    Compute a continuous liquidity score from volume percentile.

    Method
    ------
    liq_score = rank_pct(Volume)

    Parameters
    ----------
    df : pd.DataFrame
        Must contain ["Volume"].
    period : int, default=20
        (Unused in this global percentile; kept for API symmetry.)

    Returns
    -------
    pd.Series
        Liquidity score.

    Value Range
    -----------
    [0.0, 1.0]
      • 0.0 = lowest volume in sample
      • 1.0 = highest volume in sample

    Notes
    -----
    - Percentile is computed across the full series (not rolling).
    """
    liq_score = df["Volume"].rank(pct=True)
    return liq_score


def _compute_market_stress(df, period=20):
    """
    Compute a continuous market stress score based on Bollinger Band width percentile.

    Method
    ------
    bb_width     = (Upper - Lower) / SMA
    stress_score = rank_pct(bb_width)

    Parameters
    ----------
    df : pd.DataFrame
        Must contain ["Close"].
    period : int, default=20
        Bollinger calculation window.

    Returns
    -------
    pd.Series
        Stress score.

    Value Range
    -----------
    [0.0, 1.0]
      • Higher values indicate volatility expansion / stress

    Notes
    -----
    - Percentile computed across the series (not rolling).
    """
    bb_width = _compute_bollinger_width(df["Close"], period)
    stress_score = pd.Series(bb_width, index=df.index).rank(pct=True)
    return stress_score


def _compute_composite_regime_score(df):
    """
    Compute a composite regime score combining volatility, trend, and liquidity.

    Method
    ------
    Given:
      Volatility_Regime in [0, 1]
      Trend_Regime      in [-1, 1]
      Liquidity_Regime  in [0, 1]

    Transform:
      trend_abs = |Trend_Regime|

    Composite (example weights):
      score = 0.4 * Volatility_Regime + 0.4 * trend_abs + 0.2 * Liquidity_Regime

    Parameters
    ----------
    df : pd.DataFrame
        Must contain columns:
          - "Volatility_Regime"
          - "Trend_Regime"
          - "Liquidity_Regime"

    Returns
    -------
    pd.Series
        Composite score per bar.

    Value Range
    -----------
    [0.0, 1.0]
      • Higher → more extreme market state: volatile, liquid, and strongly trending.

    Notes
    -----
    - Weights (0.4/0.4/0.2) are heuristic; adjust to fit your use case.
    """
    vol_score = df["Volatility_Regime"].clip(0, 1).fillna(0)
    liq_score = df["Liquidity_Regime"].clip(0, 1).fillna(0)
    trend_score = df["Trend_Regime"].abs().clip(0, 1).fillna(0)
    composite_score = 0.4 * vol_score + 0.4 * trend_score + 0.2 * liq_score
    return composite_score


def _compute_garman_klass_volatility(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """
    Garman–Klass Volatility (range-based).

    Definition
    ----------
    rs_t = 0.5 * (ln(H/L))^2 - (2ln2 - 1) * (ln(C/O))^2
    σ_GK = sqrt(mean(rs, period))

    Parameters
    ----------
    df : pd.DataFrame
        Columns: 'Open','High','Low','Close'.
    period : int, default 20

    Returns
    -------
    pd.Series
        Garman–Klass volatility.

    Value Range
    -----------
    [0, +∞) — not annualized (scale if required).
    """
    log_hl = np.log(df["High"] / df["Low"])
    log_co = np.log(df["Close"] / df["Open"])
    rs = 0.5 * log_hl ** 2 - (2 * np.log(2) - 1) * (log_co ** 2)
    vol = np.sqrt(rs.rolling(period).mean().clip(lower=0.0))
    vol.name = "GK_Vol"
    return vol


def _compute_parkinson_volatility(df: pd.DataFrame, period: int = 20) -> pd.Series:
    """
    Parkinson Volatility (high–low range).

    Definition
    ----------
    σ_P = sqrt( mean( (ln(H/L))^2, period ) / (4 ln 2) )

    Parameters
    ----------
    df : pd.DataFrame
        Columns: 'High','Low'.
    period : int, default 20

    Returns
    -------
    pd.Series
        Parkinson volatility.

    Value Range
    -----------
    [0, +∞).
    """
    rs = (np.log(df["High"] / df["Low"])) ** 2
    vol = np.sqrt(rs.rolling(period).mean() / (4.0 * np.log(2.0)))
    vol.name = "Parkinson_Vol"
    return vol


# ==========================================
# ===== Fractal / Complexity Indicators =====
# ==========================================
def _as_series(x: pd.Series, name: str) -> pd.Series:
    """Ensure Pandas Series with a name."""
    s = pd.Series(x) if not isinstance(x, pd.Series) else x.copy()
    if s.name is None:
        s.name = name
    return s

def _compute_hurst_exponent(series: pd.Series, lags = (2, 4, 8, 16, 32)) -> pd.Series:
    """
    Hurst Exponent H via variance scaling of differences (rolling).

    Definition
    ----------
    Var(X_t - X_{t-lag}) ∝ lag^{2H}
    Fit slope m on log-lag vs log(std(diff_lag)); H = m.

    Parameters
    ----------
    series : pd.Series
        Price series.
    lags : sequence of int, default (2,4,8,16,32)
        Lags to use for slope.

    Returns
    -------
    pd.Series
        Rolling H estimate (aligned with last lag window).

    Value Range
    -----------
    (0, 1) — <0.5 mean-reverting; ≈0.5 random; >0.5 trending.

    Notes
    -----
    Uses a rolling window equal to max(lags)*2 to stabilize estimates.
    """
    series = _as_series(series, "Close")
    max_lag = int(max(lags))
    win = max_lag * 2

    def _calc(idx):
        s = series.iloc[idx - win:idx]
        if len(s) < win:
            return np.nan
        tau = []
        for lag in lags:
            dd = s.diff(lag).dropna()
            tau.append(dd.std())
        if np.any(np.array(tau) <= 0):
            return np.nan
        m, _ = np.polyfit(np.log(lags), np.log(tau), 1)
        return float(m)

    out = pd.Series(np.nan, index=series.index, name="Hurst")
    for i in range(win, len(series) + 1):
        out.iloc[i - 1] = _calc(i)
    return out


def _compute_katz_fractal_dimension(series: pd.Series, period: int = 60) -> pd.Series:
    """
    Katz Fractal Dimension (rolling).

    Definition
    ----------
    D = log10(n) / (log10(n) + log10(d/L)),
    n: points in window, d: max distance from first point, L: path length.

    Parameters
    ----------
    series : pd.Series
        Price series.
    period : int, default 60

    Returns
    -------
    pd.Series
        Katz FD.

    Value Range
    -----------
    [1, 2] — 1: linear trend; 2: noisy/random.
    """
    series = _as_series(series, "Close")

    def _katz(x):
        n = len(x)
        L = np.sum(np.abs(np.diff(x)))
        d = np.max(np.abs(x - x[0])) if n > 1 else 0.0
        if L <= 0 or d <= 0:
            return np.nan
        return np.log10(n) / (np.log10(n) + np.log10(d / L))

    return series.rolling(period).apply(lambda x: _katz(np.asarray(x)), raw=False).rename("Katz_FD")


def _compute_approximate_entropy(series: pd.Series, m: int = 2, r: float = 0.2, period: int = 120) -> pd.Series:
    """
    Approximate Entropy (ApEn) — rolling regularity measure.

    Definition
    ----------
    ApEn(m, r) = Φ^m(r) - Φ^{m+1}(r), computed over rolling window.

    Parameters
    ----------
    series : pd.Series
        Scalar series (e.g., returns).
    m : int, default 2
        Embedding dimension.
    r : float, default 0.2
        Tolerance as fraction of window std.
    period : int, default 120
        Rolling window.

    Returns
    -------
    pd.Series
        ApEn series.

    Value Range
    -----------
    [0, +∞) — higher → more randomness.
    """
    series = _as_series(series, "X")

    def _apen(x):
        x = np.asarray(x, dtype=float)
        sd = np.std(x)
        if sd == 0:
            return 0.0
        tol = r * sd
        N = len(x)

        def _phi(m):
            if N - m + 1 <= 1:
                return np.nan
            emb = np.array([x[i:i + m] for i in range(N - m + 1)])
            # Chebyshev distance
            dist = np.max(np.abs(emb[:, None, :] - emb[None, :, :]), axis=2)
            C = (dist <= tol).mean(axis=0)
            C = C[C > 0]
            return np.mean(np.log(C))

        a = _phi(m)
        b = _phi(m + 1)
        return (a - b) if (a is not None and b is not None) else np.nan

    return series.rolling(period).apply(_apen, raw=False).rename("ApEn")


def _compute_permutation_entropy(series: pd.Series, order: int = 3, delay: int = 1, period: int = 120) -> pd.Series:
    """
    Permutation Entropy (rolling), invariant to monotonic transforms.

    Parameters
    ----------
    series : pd.Series
        Scalar series.
    order : int, default 3
        Ordinal pattern length.
    delay : int, default 1
        Time delay between samples forming a pattern.
    period : int, default 120
        Rolling window length.

    Returns
    -------
    pd.Series
        Normalized permutation entropy.

    Value Range
    -----------
    [0, 1] — 1 is maximum randomness (Shannon normalized by log(order!)).
    """
    import itertools, math
    series = _as_series(series, "X")
    patterns = list(itertools.permutations(range(order)))

    def _perm_entropy(x):
        x = np.asarray(x)
        n = len(x) - delay * (order - 1)
        if n <= 1:
            return np.nan
        counts = {p: 0 for p in patterns}
        for i in range(n):
            pat = tuple(np.argsort(x[i:i + delay * order:delay]))
            counts[pat] += 1
        p = np.array(list(counts.values()), dtype=float)
        p = p / p.sum()
        p = p[p > 0]
        return (-np.sum(p * np.log(p)) / np.log(math.factorial(order)))


    return series.rolling(period).apply(_perm_entropy, raw=False).rename("PermEn")


def _compute_fractal_dimension_from_hurst(series: pd.Series, period: int = 120) -> pd.Series:
    """
    Fractal Dimension via FD = 2 - H (rolling).

    Parameters
    ----------
    series : pd.Series
        Price series.
    period : int, default 120
        Internally uses H computed with lags up to ~period/2.

    Returns
    -------
    pd.Series
        FD series.

    Value Range
    -----------
    [1, 2] — lower is trend-dominant; higher is noise-dominant.
    """
    max_lag = max(2, period // 8)
    lags = tuple(sorted(set([2, 4, 8, 16, 32, max_lag])))
    H = _compute_hurst_exponent(series, lags=lags)
    fd = (2 - H).rename("Fractal_Dimension")
    return fd


# =========================================
# ===== Spectral / Info-Theory / Chaos =====
# =========================================

def _compute_lomb_scargle_power(series: pd.Series, freqs: np.ndarray, aggregate: str = "max") -> pd.Series:
    """
    Lomb–Scargle Spectral Power (rolling summary).

    Parameters
    ----------
    series : pd.Series
        Scalar series (e.g., returns or price).
    freqs : np.ndarray
        Frequencies to evaluate.
    aggregate : {'max','sum','mean'}, default 'max'
        How to summarize power across freqs per window.

    Returns
    -------
    pd.Series
        Rolling spectral power summary.

    Value Range
    -----------
    [0, +∞).

    Notes
    -----
    Requires `astropy`. If unavailable, returns NaNs with a warning.
    """

    series = _as_series(series, "X")
    win = max(60, int(2 * (1 / (freqs.min() + 1e-9))))  # heuristic

    def _ls(x):
        t = np.arange(len(x))
        p = LombScargle(t, x).power(freqs)
        if aggregate == "max":
            return float(np.nanmax(p))
        elif aggregate == "sum":
            return float(np.nansum(p))
        else:
            return float(np.nanmean(p))

    return series.rolling(win).apply(_ls, raw=False).rename("LombScargle")


def _compute_bispectrum_entropy(series: pd.Series, period: int = 256) -> pd.Series:
    """
    Bispectrum Entropy (rolling, heavy).

    Definition
    ----------
    B(f1,f2) ≈ X(f1) X(f2) X*(f1+f2); entropy computed on |B| normalized.

    Parameters
    ----------
    series : pd.Series
        Scalar series.
    period : int, default 256
        Window length (power-of-two recommended).

    Returns
    -------
    pd.Series
        Bispectrum entropy series.

    Value Range
    -----------
    [0, log(N^2)] unnormalized; here reported in natural units and scaled by log(n_bins).

    Notes
    -----
    O(N^2) per window — computationally expensive; use sparingly.
    """
    series = _as_series(series, "X")

    def _entropy(x):
        x = np.asarray(x)
        N = len(x)
        fft_vals = np.fft.fft(x)
        # Downsample freqs to reduce complexity
        step = max(1, N // 64)
        idxs = np.arange(0, N, step)
        B = []
        for i in idxs:
            for j in idxs:
                k = (i + j) % N
                B.append(fft_vals[i] * fft_vals[j] * np.conj(fft_vals[k]))
        mag = np.abs(B)
        if mag.sum() == 0:
            return 0.0
        p = mag / mag.sum()
        p = p[p > 0]
        return float(-np.sum(p * np.log(p)) / np.log(len(p)))

    return series.rolling(period).apply(_entropy, raw=False).rename("Bispec_Entropy")


def _compute_renyi_entropy(series: pd.Series, alpha: float = 2.0, bins: int = 32, period: int = 120) -> pd.Series:
    """
    Rényi Entropy H_α (rolling, histogram-based).

    Definition
    ----------
    H_α = 1/(1-α) * log(Σ p_i^α), α>0, α≠1

    Parameters
    ----------
    series : pd.Series
        Scalar series.
    alpha : float, default 2.0
    bins : int, default 32
    period : int, default 120

    Returns
    -------
    pd.Series
        Rényi entropy (normalized by log(bins)).

    Value Range
    -----------
    [0, 1] when normalized by log(bins).
    """
    series = _as_series(series, "X")

    def _renyi(x):
        hist, _ = np.histogram(x, bins=bins, density=True)
        p = hist[hist > 0]
        if len(p) == 0:
            return np.nan
        return float((1.0 / (1.0 - alpha)) * np.log(np.sum(p ** alpha)) / np.log(bins))

    return series.rolling(period).apply(_renyi, raw=False).rename("Renyi_Entropy")


def _compute_rolling_kl_divergence(
    series: pd.Series,
    window: int = 30,
    bins: int = 32,
    eps: float = 1e-9
) -> pd.Series:
    """
    Rolling Kullback–Leibler (KL) divergence comparing two adjacent windows of returns.

    Purpose
    -------
    Compute D_KL(P || Q) where P = empirical distribution of returns over the *recent*
    window and Q = empirical distribution of returns over the *previous* window of the same length.
    This highlights recent distributional shifts (volatility/shape changes).

    Implementation details
    ----------------------
    - At time index t the function forms:
        P_t = histogram( returns[t-window+1 : t+1] )
        Q_t = histogram( returns[t-2*window+1 : t-window+1] )
      and computes KL(P_t || Q_t).
    - If insufficient data to form both windows, returns NaN.
    - Uses `density=True` histograms and adds `eps` to avoid log(0).
    - Histograms use shared bin edges computed over the union of both windows to ensure comparable supports.

    Parameters
    ----------
    series : pd.Series
        Price series (Close). The function uses percentage changes internally.
    window : int, default=30
        Window length (in observations) for each distribution (recent & previous).
    bins : int, default=32
        Number of histogram bins.
    eps : float, default=1e-9
        Small constant to avoid division by zero / log(0).

    Returns
    -------
    pd.Series
        Rolling KL divergence (D_KL(P || Q)), indexed like `series`.
        NaN for indices where not enough historical data exists.

    Value Range
    -----------
    [0, +∞) — 0 indicates identical empirical distributions.

    Notes
    -----
    - KL is not symmetric. You can swap arguments if you prefer Q||P.
    - Choice of bins and window strongly affects sensitivity; tune for your timeframe.
    """
    returns = series.pct_change().replace([np.inf, -np.inf], np.nan).dropna()
    out = pd.Series(np.nan, index=series.index, name=f"KL_win{window}_bins{bins}")

    # only compute when we have at least 2*window points up to index i
    total_len = len(series)
    for i in range(2 * window - 1, total_len):
        recent_idx_start = i - window + 1
        prev_idx_start = i - 2 * window + 1
        recent = returns.iloc[recent_idx_start: i + 1]
        prev = returns.iloc[prev_idx_start: recent_idx_start]
        if len(recent) < window or len(prev) < window:
            out.iloc[i] = np.nan
            continue
        # combined bin edges
        all_vals = np.concatenate([recent.values, prev.values])
        try:
            hist_all, edges = np.histogram(all_vals, bins=bins, density=True)
            # compute histograms with same edges
            p_hist, _ = np.histogram(recent.values, bins=edges, density=True)
            q_hist, _ = np.histogram(prev.values, bins=edges, density=True)
            p = p_hist + eps
            q = q_hist + eps
            p = p / p.sum()
            q = q / q.sum()
            kl = np.sum(p * np.log(p / q))
            out.iloc[i] = float(kl)
        except Exception:
            out.iloc[i] = np.nan

    return out




def _compute_lyapunov_exponent(series: pd.Series, m: int = 5, tau: int = 1, period: int = 200) -> pd.Series:
    """
    Largest Lyapunov Exponent (rolling, approximate).

    Parameters
    ----------
    series : pd.Series
        Scalar series.
    m : int, default 5
        Embedding dimension.
    tau : int, default 1
        Delay.
    period : int, default 200
        Rolling window for local estimation.

    Returns
    -------
    pd.Series
        Lyapunov exponent estimate.

    Value Range
    -----------
    (-∞, +∞) — >0 suggests chaos, <0 suggests stability.

    Notes
    -----
    Requires `scipy` for KDTree. If unavailable, returns NaNs with a warning.
    """

    series = _as_series(series, "X")
    emb_dim = m
    delay = tau

    def _lyap(x):
        x = np.asarray(x, dtype=float)
        N = len(x) - (emb_dim - 1) * delay
        if N <= emb_dim + 1:
            return np.nan
        # Phase-space reconstruction
        Y = np.array([x[i:i + N] for i in range(0, emb_dim * delay, delay)]).T
        tree = KDTree(Y)
        d, idx = tree.query(Y, k=2)
        # Exclude self
        nn = idx[:, 1]
        dist0 = d[:, 1]
        # Avoid zeros
        dist0 = np.where(dist0 <= 1e-12, np.nan, dist0)
        valid = ~np.isnan(dist0)
        if valid.sum() < 5:
            return np.nan
        # Simple average log expansion at 1-step
        lam = np.log(dist0[valid]).mean()
        return float(lam)

    return series.rolling(period).apply(_lyap, raw=False).rename("Lyapunov")


def _compute_dfa_scaling_exponent(series: pd.Series, period: int = 240) -> pd.Series:
    """
    Detrended Fluctuation Analysis (DFA) scaling exponent α (rolling).

    Parameters
    ----------
    series : pd.Series
        Scalar series (e.g., returns).
    period : int, default 240
        Rolling window.

    Returns
    -------
    pd.Series
        DFA scaling exponent.

    Value Range
    -----------
    (0, 2) — <0.5 anti-persistent; ≈0.5 random; >0.5 persistent.
    """
    series = _as_series(series, "X")

    def _dfa(x):
        x = np.asarray(x, dtype=float)
        N = len(x)
        y = np.cumsum(x - x.mean())
        scales = np.unique(np.logspace(1, np.log10(max(8, N // 4)), 8, dtype=int))
        F = []
        for s in scales:
            nseg = N // s
            if nseg < 2:
                continue
            rms = []
            for v in range(nseg):
                idx = slice(v * s, (v + 1) * s)
                t = np.arange(s)
                coeff = np.polyfit(t, y[idx], 1)
                trend = np.polyval(coeff, t)
                rms.append(np.sqrt(np.mean((y[idx] - trend) ** 2)))
            F.append(np.mean(rms))
        if len(F) < 2:
            return np.nan
        a, _ = np.polyfit(np.log(scales[:len(F)]), np.log(F), 1)
        return float(a)

    return series.rolling(period).apply(_dfa, raw=False).rename("DFA_alpha")


def _compute_multifractal_dfa(series: pd.Series, q: float = 2.0, period: int = 240) -> pd.Series:
    """
    Multifractal DFA scaling exponent H(q) (rolling).

    Parameters
    ----------
    series : pd.Series
        Scalar series.
    q : float, default 2.0
        Generalized moment.
    period : int, default 240

    Returns
    -------
    pd.Series
        H(q) scaling exponent.

    Value Range
    -----------
    (-∞, +∞) — varies with q for multifractals.
    """
    series = _as_series(series, "X")

    def _mfdxa(x):
        x = np.asarray(x, dtype=float)
        N = len(x)
        y = np.cumsum(x - x.mean())
        scales = np.unique(np.logspace(1, np.log10(max(8, N // 4)), 8, dtype=int))
        Fq = []
        for s in scales:
            nseg = N // s
            if nseg < 2:
                continue
            fseg = []
            for v in range(nseg):
                idx = slice(v * s, (v + 1) * s)
                t = np.arange(s)
                coeff = np.polyfit(t, y[idx], 1)
                detr = y[idx] - np.polyval(coeff, t)
                fseg.append(np.sqrt(np.mean(detr ** 2)))
            fseg = np.asarray(fseg)
            if q == 0:
                Fq.append(np.exp(np.mean(np.log(fseg + 1e-12))))
            else:
                Fq.append((np.mean(fseg ** q)) ** (1.0 / q))
        if len(Fq) < 2:
            return np.nan
        a, _ = np.polyfit(np.log(scales[:len(Fq)]), np.log(Fq), 1)
        return float(a)

    return series.rolling(period).apply(_mfdxa, raw=False).rename("MF_DFA_Hq")


# ====================================
# ===== Inter-Series / Econometrics ===
# ====================================

def _compute_rolling_beta(df: pd.DataFrame, benchmark: pd.Series, period: int = 60) -> pd.Series:
    """
    Rolling Beta vs benchmark.

    Definition
    ----------
    β = Cov(R_asset, R_bench) / Var(R_bench)

    Parameters
    ----------
    df : pd.DataFrame
        Must contain 'Close'.
    benchmark : pd.Series
        Benchmark Close (aligned).
    period : int, default 60

    Returns
    -------
    pd.Series
        Rolling beta.

    Value Range
    -----------
    (-∞, +∞).
    """
    r = df["Close"].pct_change()
    rb = benchmark.pct_change()
    cov = r.rolling(period).cov(rb)
    var = rb.rolling(period).var()
    beta = cov / var.replace(0, np.nan)
    beta.name = "Beta"
    return beta


def _compute_rolling_alpha(df: pd.DataFrame, benchmark: pd.Series, period: int = 60) -> pd.Series:
    """
    Rolling Alpha vs benchmark.

    Definition
    ----------
    α = R_asset - β * R_bench

    Parameters
    ----------
    df : pd.DataFrame
        Must contain 'Close'.
    benchmark : pd.Series
        Benchmark Close (aligned).
    period : int, default 60

    Returns
    -------
    pd.Series
        Rolling alpha (simple excess return).

    Value Range
    -----------
    (-∞, +∞).
    """
    beta = _compute_rolling_beta(df, benchmark, period)
    r = df["Close"].pct_change()
    rb = benchmark.pct_change()
    alpha = r - beta * rb
    alpha.name = "Alpha"
    return alpha


def _compute_cross_sample_entropy(series1: pd.Series, series2: pd.Series, m: int = 2, r: float = 0.2,
                                  period: int = 120) -> pd.Series:
    """
    Cross-Sample Entropy (rolling).

    Parameters
    ----------
    series1, series2 : pd.Series
        Two scalar series (aligned).
    m : int, default 2
        Embedding dimension.
    r : float, default 0.2
        Tolerance as fraction of window std (per series).
    period : int, default 120
        Rolling window.

    Returns
    -------
    pd.Series
        Cross-sample entropy.

    Value Range
    -----------
    [0, +∞) — lower implies greater synchrony.
    """
    s1 = _as_series(series1, "X1")
    s2 = _as_series(series2, "X2")

    def _xsampen(x, y):
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        N = len(x)
        if N < m + 2:
            return np.nan
        tol = r * 0.5 * (np.std(x) + np.std(y))

        def _count(m):
            embx = np.array([x[i:i + m] for i in range(N - m + 1)])
            emby = np.array([y[i:i + m] for i in range(N - m + 1)])
            dist = np.max(np.abs(embx[:, None, :] - emby[None, :, :]), axis=2)
            return np.sum(dist <= tol)

        A = _count(m + 1)
        B = _count(m)
        if B == 0 or A == 0:
            return np.nan
        return float(-np.log(A / B))

    out = pd.Series(np.nan, index=s1.index, name="CrossSampEn")
    for i in range(period, len(s1) + 1):
        out.iloc[i - 1] = _xsampen(s1.iloc[i - period:i], s2.iloc[i - period:i])
    return out


def _compute_largest_lagged_correlation(series1: pd.Series, series2: pd.Series, max_lag: int = 50) -> float:
    """
    Largest absolute lagged correlation over ±max_lag.

    Parameters
    ----------
    series1, series2 : pd.Series
        Two aligned series.
    max_lag : int, default 50

    Returns
    -------
    float
        Maximum absolute Pearson correlation across lags.

    Value Range
    -----------
    [0, 1].
    """
    s1 = series1.values
    s2 = series2.values
    best = 0.0
    n = len(s1)
    for lag in range(-max_lag, max_lag + 1):
        if lag < 0:
            a, b = s1[-lag:], s2[:n + lag]
        elif lag > 0:
            a, b = s1[:n - lag], s2[lag:]
        else:
            a, b = s1, s2
        if len(a) < 3:
            continue
        c = np.corrcoef(a, b)[0, 1]
        if np.isfinite(c):
            best = max(best, abs(c))
    return float(best)


def _compute_garch_volatility(returns: pd.Series, p: int = 1, q: int = 1) -> pd.Series:
    """
    GARCH(p,q) conditional volatility (fitted, in-sample).

    Parameters
    ----------
    returns : pd.Series
        Return series (e.g., daily log or pct returns).
    p, q : int, default 1
        GARCH orders.

    Returns
    -------
    pd.Series
        Conditional volatility (same index as returns).

    Value Range
    -----------
    (0, +∞).

    Notes
    -----
    Requires `arch`. If unavailable, returns NaNs with a warning.
    """

    r = returns.dropna()
    model = arch_model(r, vol="GARCH", p=p, q=q, rescale=False)
    res = model.fit(disp="off")
    vol = res.conditional_volatility.reindex(returns.index)
    vol.name = "GARCH_Vol"
    return vol


# ====================================
# ===== Additional Dynamics Metrics ===
# ====================================

def _compute_price_entropy(series: pd.Series, bins: int = 10, period: int = 120) -> pd.Series:
    """
    Shannon entropy of return distribution (rolling).

    Parameters
    ----------
    series : pd.Series
        Price series (Close).
    bins : int, default 10
        Histogram bins.
    period : int, default 120

    Returns
    -------
    pd.Series
        Entropy normalized by log(bins).

    Value Range
    -----------
    [0, 1] (normalized).
    """
    series = _as_series(series, "Close")
    ret = series.pct_change()

    def _ent(x):
        hist, _ = np.histogram(x, bins=bins, density=True)
        p = hist[hist > 0]
        if p.size == 0:
            return np.nan
        return float(-np.sum(p * np.log(p)) / np.log(bins))

    return ret.rolling(period).apply(_ent, raw=False).rename("Price_Entropy")


def _compute_price_velocity(series: pd.Series, period: int = 5) -> pd.Series:
    """
    Price velocity (finite difference per bar).

    Definition
    ----------
    v_t = (P_t - P_{t-period}) / period

    Parameters
    ----------
    series : pd.Series
        Price series.
    period : int, default 5

    Returns
    -------
    pd.Series
        Velocity.

    Value Range
    -----------
    (-∞, +∞).
    """
    v = (series - series.shift(period)) / float(period)
    v.name = f"Velocity_{period}"
    return v


def _compute_price_acceleration(series: pd.Series, period: int = 5) -> pd.Series:
    """
    Price acceleration (change in velocity).

    Definition
    ----------
    a_t = v_t - v_{t-1}

    Parameters
    ----------
    series : pd.Series
        Price series.
    period : int, default 5

    Returns
    -------
    pd.Series
        Acceleration.

    Value Range
    -----------
    (-∞, +∞).
    """
    acc = _compute_price_velocity(series, period).diff()
    acc.name = f"Acceleration_{period}"
    return acc


def _compute_absolute_price_change(series: pd.Series, period: int = 1) -> pd.Series:
    """
    Absolute price change over `period`.

    Parameters
    ----------
    series : pd.Series
        Price series.
    period : int, default 1

    Returns
    -------
    pd.Series
        |P_t - P_{t-period}|.

    Value Range
    -----------
    [0, +∞).
    """
    apc = (series - series.shift(period)).abs()
    apc.name = f"AbsChange_{period}"
    return apc


def _compute_coppock_curve(series: pd.Series, wma_period: int = 10) -> pd.Series:
    """
    Coppock Curve (long-term momentum).

    Definition
    ----------
    CC = WMA(ROC_14 + ROC_11, wma_period), ROC in percent.

    Parameters
    ----------
    series : pd.Series
        Price series.
    wma_period : int, default 10

    Returns
    -------
    pd.Series
        Coppock curve.

    Value Range
    -----------
    (-∞, +∞).
    """
    roc_14 = series.pct_change(14) * 100.0
    roc_11 = series.pct_change(11) * 100.0
    cc = roc_14 + roc_11
    weights = np.arange(1, wma_period + 1, dtype=float)

    def _wma(x):
        return float(np.dot(x, weights) / weights.sum())

    return cc.rolling(wma_period).apply(_wma, raw=True).rename("Coppock")


# -----------------------------
# Rolling Largest Lagged Correlation
# -----------------------------
def _compute_rolling_largest_lagged_correlation(
    series_x: pd.Series,
    series_y: pd.Series,
    window: int = 120,
    max_lag: int = 10,
) -> pd.Series:
    """
    Rolling largest absolute Pearson correlation across ±lags between two series.

    Purpose
    -------
    For each rolling window (length `window`), search integer lags in [-max_lag, max_lag]
    and compute Pearson correlation between appropriately shifted slices of the two series.
    Return the maximum absolute correlation found (and optionally the lag could be stored separately).

    Implementation details
    ----------------------
    - For a specific window ending at t, the function considers x_window and y_window slices
      and calculates corr(x_window[:-lag], y_window[lag:]) for positive lag,
      corr(x_window[-lag:], y_window[:-lag]) for negative lag, etc.
    - Uses a fast vectorized approach where possible; falls back to loop for clarity.

    Parameters
    ----------
    series_x : pd.Series
        First series (e.g., asset returns or close).
    series_y : pd.Series
        Second series (e.g., benchmark returns). Must be aligned index-wise to series_x.
    window : int, default=120
        Rolling window length.
    max_lag : int, default=10
        Max lag (in bars) to consider in either direction.

    Returns
    -------
    pd.Series
        Rolling largest absolute lagged correlation (values in [0, 1]) indexed like `series_x`.
        NaN for early indices with insufficient data.

    Value Range
    -----------
    [0, 1] — absolute Pearson correlation.

    Notes
    -----
    - If series contain NaNs in a window, that window produces NaN unless enough non-NaN pairs remain.
    - Use returns or log-returns instead of raw prices for more meaningful correlations.
    """
    x = series_x.copy()
    y = series_y.copy()
    n = len(x)
    out = pd.Series(np.nan, index=x.index, name=f"LaggedCorr_win{window}_lag{max_lag}")

    for end in range(window - 1, n):
        start = end - window + 1
        xw = x.iloc[start:end + 1].values
        yw = y.iloc[start:end + 1].values
        if np.isnan(xw).any() or np.isnan(yw).any():
            # attempt to drop NaNs pairwise
            mask = np.isfinite(xw) & np.isfinite(yw)
            xw = xw[mask]; yw = yw[mask]
        if len(xw) < max(10, window // 4):
            out.iloc[end] = np.nan
            continue

        best = 0.0
        # check lags from -max_lag to +max_lag
        for lag in range(-max_lag, max_lag + 1):
            if lag == 0:
                a = xw; b = yw
            elif lag > 0:
                a = xw[:-lag]; b = yw[lag:]
            else:  # lag < 0
                a = xw[-lag:]; b = yw[:lag]
            if len(a) < 3:
                continue
            c = np.corrcoef(a, b)[0, 1]
            if np.isfinite(c):
                best = max(best, abs(c))
        out.iloc[end] = float(best)
    return out


# -----------------------------
# Rolling Cross-Sample Entropy
# -----------------------------
def _compute_rolling_cross_sample_entropy(
    series_x: pd.Series,
    series_y: pd.Series,
    m: int = 2,
    r_factor: float = 0.2,
    window: int = 120
) -> pd.Series:
    """
    Rolling Cross-Sample Entropy (Cross-SampEn) between two aligned series.

    Purpose
    -------
    Measures synchrony / shared regularity between two signals. Lower values indicate
    higher similarity/synchrony; higher values indicate dissimilarity.

    Implementation details
    ----------------------
    - For each rolling window of length `window` ending at t, compute Cross-SampEn:
        CrossSampEn(m, r) = -log( A / B )
      where A = number of matching template pairs of length m+1 (cross-matches),
            B = number of matching template pairs of length m.
    - Distance metric: Chebyshev (max absolute difference) between embedding vectors.
    - Tolerance r = r_factor * std(windowed series) (uses average std of the two series).
    - If counts lead to undefined log (A==0 or B==0), return NaN.

    Parameters
    ----------
    series_x : pd.Series
        First series (aligned).
    series_y : pd.Series
        Second series (aligned).
    m : int, default 2
        Embedding length.
    r_factor : float, default 0.2
        Tolerance multiplier applied to average window std.
    window : int, default 120
        Rolling window length.

    Returns
    -------
    pd.Series
        Rolling Cross-Sample Entropy (non-negative), indexed like inputs.

    Value Range
    -----------
    [0, +∞) — 0 indicates perfect synchrony in patterns.

    Notes
    -----
    - Computationally heavier than simple correlations; window and m should be tuned.
    - If series have substantial NaNs in a window, that position yields NaN.
    """
    x = series_x.copy()
    y = series_y.copy()
    n = len(x)
    out = pd.Series(np.nan, index=x.index, name=f"CrossSampEn_m{m}_w{window}")

    for end in range(window - 1, n):
        start = end - window + 1
        xw = x.iloc[start:end + 1].values
        yw = y.iloc[start:end + 1].values
        mask = np.isfinite(xw) & np.isfinite(yw)
        xw = xw[mask]; yw = yw[mask]
        N = len(xw)
        if N < m + 2:
            out.iloc[end] = np.nan
            continue

        sd_avg = 0.5 * (np.std(xw) + np.std(yw))
        tol = r_factor * (sd_avg if sd_avg > 0 else 1e-8)

        # Build embedded templates
        emb_x_m = np.array([xw[i:i + m] for i in range(N - m + 1)])
        emb_y_m = np.array([yw[i:i + m] for i in range(N - m + 1)])
        emb_x_m1 = np.array([xw[i:i + (m + 1)] for i in range(N - (m + 1) + 1)])
        emb_y_m1 = np.array([yw[i:i + (m + 1)] for i in range(N - (m + 1) + 1)])

        # Count matches
        # For Chebyshev distance, use max absolute difference across embedding dims
        def count_cross_matches(A, B, tol):
            # A: nA x d, B: nB x d
            if A.size == 0 or B.size == 0:
                return 0
            # Efficient pairwise max absolute diff using broadcasting (may be memory heavy)
            dists = np.max(np.abs(A[:, None, :] - B[None, :, :]), axis=2)
            return int(np.sum(dists <= tol))

        B_count = count_cross_matches(emb_x_m, emb_y_m, tol)
        A_count = count_cross_matches(emb_x_m1, emb_y_m1, tol)

        if B_count == 0 or A_count == 0:
            out.iloc[end] = np.nan
        else:
            out.iloc[end] = float(-np.log(A_count / B_count))
    return out

def _compute_daily_sector_median_returns(mapping_df, returns_df,
                                        ticker_column_name, datetime_column_name,
                                        sector_column_name, returns_column_name,
                                        output_file=None):
    """
    Compute daily median sector returns based on company-to-sector mapping and
    company-level daily returns.

    Parameters
    ----------
    mapping_file : str
        Path to the CSV containing company-to-sector mapping.
        Must contain at least: ['Symbol', 'Sector']

    returns_file : str
        Path to the CSV containing daily returns of companies.
        Must contain at least: ['Date', 'Symbol', 'Return']

    output_file : str, optional
        If provided, saves the resulting sector median returns to this CSV file.

    Returns
    -------
    pd.DataFrame
        DataFrame with ['Date', 'Sector', 'Median_Return'].
    """

    # Load the mapping and returns
    # Ensure correct column naming

    # Merge returns with sector mapping

    merged_df = returns_df.merge(mapping_df, on=ticker_column_name, how="left")
    # Group by Date + Sector and compute median
    sector_median = (
        merged_df
        .groupby([datetime_column_name, sector_column_name])[returns_column_name]
        .median()
        .reset_index()
        .rename(columns={returns_column_name: "Median_Return"})
    )

    # Save to CSV if requested
    if output_file:
        sector_median.to_csv(output_file, index=False)

    return sector_median