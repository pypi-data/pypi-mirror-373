import hashlib
import pandas as pd
import calendar
import os
import numpy as np
import re
from .utils import (_compute_rsi, _compute_adx, _compute_atr, _compute_cci, _compute_cmf, _compute_mfi,
                   _compute_obv, _compute_stochastic, _compute_macd, _compute_vwap, _compute_williams_r,
                   _compute_bollinger_width, _compute_bollinger_position, _compute_trend_regime,
                   _compute_market_stress, _compute_liquidity_regime, _compute_volatility_regime,
                   _compute_composite_regime_score, _compute_garman_klass_volatility, _compute_garch_volatility,
                   _compute_rolling_kl_divergence, _compute_rolling_largest_lagged_correlation,
                   _compute_rolling_cross_sample_entropy, _compute_price_entropy, _compute_renyi_entropy,
                   _compute_bispectrum_entropy, _compute_approximate_entropy, _compute_permutation_entropy,
                   _compute_rolling_beta, _compute_rolling_alpha, _compute_hurst_exponent,
                   _compute_lyapunov_exponent, _compute_dfa_scaling_exponent, _compute_multifractal_dfa,
                   _compute_price_velocity, _compute_price_acceleration, _compute_absolute_price_change,
                   _compute_coppock_curve, _compute_parkinson_volatility, _compute_lomb_scargle_power,
                   _compute_katz_fractal_dimension, _compute_fractal_dimension_from_hurst, arch_model,
                   _compute_daily_sector_median_returns)


class FeatureGenerator:
    """
        A class for generating a wide range of **price-based, volume-based, and technical indicator features**
        for time series financial data, along with their changes and statistical normalizations (Z-scores).

        This class supports:
        - Calculation of **technical indicators** such as ATR, RSI, MACD, ADX, CCI, Stochastic Oscillator,
          Williams %R, OBV, CMF, MFI, VWAP, and Bollinger metrics.
        - Computation of **percentage changes** for each indicator across multiple lookback periods.
        - Computation of **rolling Z-scores** for normalized comparison.
        - Creation of **price action transformations** and statistical features like volatility, Calmar, and Sharpe ratios.

        Typical workflow:
        1. Call `compute_features(df)` on OHLCV data to compute indicators and derived changes/Z-scores.
        2. Optionally call `price_action_transformations(...)` to align features for predictive modeling.

        Attributes
        ----------
        FEATURES : list of str
            A predefined list of standard feature names that can be computed by `price_action_transformations`.
        feature_configs : list
            Optional list of configuration objects or dicts specifying custom feature computation behavior.
        cache : dict
            Internal cache mapping hashed recent OHLCV data to previously computed feature DataFrames
            to avoid recomputation.

        Notes
        -----
        **Indicator ranges** (default conventions):
        - RSI: 0 to 100 (70+ overbought, 30- oversold).
        - ADX: 0 to 100 (25+ trending, <20 weak trend).
        - ATR: Positive real number (unit = same as price).
        - CCI: Typically -200 to +200 (0 = neutral).
        - Stochastic %K, %D: 0 to 100 (80+ overbought, <20 oversold).
        - Williams %R: -100 to 0 (closer to 0 = overbought).
        - OBV: Cumulative volume metric (unbounded, unit = volume).
        - CMF: -1 to +1 (positive = accumulation, negative = distribution).
        - MFI: 0 to 100 (80+ overbought, <20 oversold).
        - VWAP: Price level (unit = price).
        - Bollinger Width: Positive real number (relative width of bands).
        - Bollinger Position: 0 (lower band) to 1 (upper band).
        """

    FEATURES = ["1D_Close_pct_change", "Overnight_returns", "3D_Close_pct_change",
        "5D_Close_pct_change", "10D_Close_pct_change", "20D_Close_pct_change", "40D_Close_pct_change",
        "60D_Close_pct_change", "125D_Close_pct_change", "252_Close_pct_change",

        "1D_Volume_pct_change", "3D_Volume_pct_change",
        "5D_Volume_pct_change", "10D_Volume_pct_change", "20D_Volume_pct_change", "40D_Volume_pct_change",
        "60D_Volume_pct_change", "125D_Volume_pct_change", "252_Volume_pct_change",

        "5D_Vol", "10D_Vol", "20D_Vol", "40D_Vol", "60D_Vol", "125D_Vol", "252_Vol", "3D_Vol",

        "5D_Calmar", "10D_Calmar", "20D_Calmar", "40D_Calmar", "60D_Calmar", "125D_Calmar", "252D_Calmar",

        "5D_Sharpe", "10D_Sharpe", "20D_Sharpe", "40D_Sharpe", "60D_Sharpe", "125D_Sharpe", "252D_Sharpe",

        "1D_Close_Z_Score_pct_change_60D_lookback", "3D_Close_Z_Score_pct_change_60D_lookback",
        "5D_Close_Z_Score_pct_change_60D_lookback", "10D_Close_Z_Score_pct_change_60D_lookback",
        "20D_Close_Z_Score_pct_change_60D_lookback", "60D_Close_Z_Score_pct_change_60D_lookback",
        "125D_Close_Z_Score_pct_change_60D_lookback", "252D_Close_Z_Score_pct_change_60D_lookback",

        "1D_Volume_Z_Score_pct_change_60D_lookback", "3D_Volume_Z_Score_pct_change_60D_lookback",
        "5D_Volume_Z_Score_pct_change_60D_lookback", "10D_Volume_Z_Score_pct_change_60D_lookback",
        "20D_Volume_Z_Score_pct_change_60D_lookback", "60D_Volume_Z_Score_pct_change_60D_lookback",
        "125D_Volume_Z_Score_pct_change_60D_lookback", "252D_Volume_Z_Score_pct_change_60D_lookback",

        "1D_Close_x_Volume_Z_Score_60D_lookback", "3D_Close_x_Volume_Z_Score_60D_lookback",
        "5D_Close_x_Volume_Z_Score_60D_lookback", "10D_Close_x_Volume_Z_Score_60D_lookback",
        "20D_Close_x_Volume_Z_Score_60D_lookback", "40D_Close_x_Volume_Z_Score_60D_lookback",
        "60D_Close_x_Volume_Z_Score_60D_lookback", "120D_Close_x_Volume_Z_Score_60D_lookback",
        "252D_Close_x_Volume_Z_Score_60D_lookback",

        "5D_Volatility_pct_change_Z_Score_60D_lookback", "10D_Volatility_pct_change_Z_Score_60D_lookback",
        "20D_Volatility_pct_change_Z_Score_60D_lookback", "40D_Volatility_pct_change_Z_Score_60D_lookback",
        "60D_Volatility_pct_change_Z_Score_60D_lookback", "120D_Volatility_pct_change_Z_Score_60D_lookback",
        "252D_Volatility_pct_change_Z_Score_60D_lookback",

        "5D_SR_pct_change_Z_Score_60D_lookback", "10D_SR_pct_change_Z_Score_60D_lookback",
        "20D_SR_pct_change_Z_Score_60D_lookback", "40D_SR_pct_change_Z_Score_60D_lookback",
        "60D_SR_pct_change_Z_Score_60D_lookback", "120D_SR_pct_change_Z_Score_60D_lookback",
        "252D_SR_pct_change_Z_Score_60D_lookback",

        "5D_CR_pct_change_Z_Score_60D_lookback", "10D_CR_pct_change_Z_Score_60D_lookback",
        "20D_CR_pct_change_Z_Score_60D_lookback", "40D_CR_pct_change_Z_Score_60D_lookback",
        "60D_CR_pct_change_Z_Score_60D_lookback", "120D_CR_pct_change_Z_Score_60D_lookback",
        "252D_CR_pct_change_Z_Score_60D_lookback",
                ]

    # Spread wrt to the Industry
    # This only provides absolute stock data. Work on a class that aggregates and gives relative data every day

    def __init__(self, feature_configs=None, benchmark = None):
        """
                Initialize the FeatureGenerator.

                Parameters
                ----------
                feature_configs : list, optional
                    A list of configuration dictionaries or objects defining custom behavior for feature
                    computation. If None, default behavior is used.
        """
        self.feature_configs = feature_configs or []
        self.cache = {}
        self.benchmark = benchmark


    def _hash_df(self, df, cols):
        """
               Create an MD5 hash representing the last 20 rows of selected columns from a DataFrame.

               This hash is used to cache computations and avoid recomputing features if the recent
               OHLCV data has not changed.

               Parameters
               ----------
               df : pd.DataFrame
                   DataFrame containing at least the columns listed in `cols`.
               cols : list of str
                   List of column names to include in the hash calculation.

               Returns
               -------
               str
                   MD5 hash string uniquely identifying the recent data subset.

               Notes
               -----
               - Only the last 20 rows are used to keep the hash computation efficient.
               - The `feature_configs` attribute is also included in the hash to ensure cache invalidation
                 when feature configurations change.
        """

        # Use only recent rows to reduce hash size
        concat_str = "".join([str(df[c].values[-20:]) for c in cols if c in df])
        return hashlib.md5((concat_str + str(self.feature_configs)).encode()).hexdigest()

    def compute_features(self, df):
        """
               Compute a set of **technical indicators** and their rolling statistics for a given OHLCV DataFrame.

               Parameters
               ----------
               df : pd.DataFrame
                   Input DataFrame with at least the following columns:
                   - 'Open', 'High', 'Low', 'Close', 'Volume'.

               Returns
               -------
               pd.DataFrame
                   Original DataFrame with new columns containing:
                   - ATR (periods: 5, 10, 14, 20) and rolling mean/std
                   - RSI (periods: 14, 28)
                   - MACD, MACD Signal, MACD Histogram
                   - ADX
                   - CCI
                   - Stochastic %K and %D
                   - Williams %R
                   - OBV
                   - CMF
                   - MFI
                   - VWAP and VWAP deviation
                   - Bollinger Width and Position
                   - For each indicator: percentage changes and Z-scores across multiple lookback periods

               Indicator Ranges
               ----------------
               - ATR: >0, same units as price
               - RSI: 0–100
               - MACD: Unbounded (price units)
               - ADX: 0–100
               - CCI: Typically -200 to +200
               - Stochastic %K, %D: 0–100
               - Williams %R: -100 to 0
               - OBV: Unbounded (volume units)
               - CMF: -1 to +1
               - MFI: 0–100
               - VWAP: Price units
               - Bollinger Width: >0 (percentage of price)
               - Bollinger Position: 0–1
        """
        df = df.copy()
        key = self._hash_df(df, ["Close", "High", "Low", "Volume"])
        if key in self.cache:
            return self.cache[key]
        feature_cols = []
        for period in [5, 10, 14, 20]:
            df[f"ATR_{period}D"] = _compute_atr(df, period)
            df[f"ATR_moving_avg_{period}D"] = df[f"ATR_{period}D"].rolling(period).mean()
            df[f"ATR_moving_std_{period}D"] = df[f"ATR_{period}D"].rolling(period).std()
            feature_cols.extend([f"ATR_{period}D", f"ATR_moving_avg_{period}D",
                                f"ATR_moving_std_{period}D"])

            # TECHNICAL INDICATORS
        for period in [14, 28]:
            df[f"RSI_{period}"] = _compute_rsi(df["Close"], period)
            feature_cols.append(f"RSI_{period}")

        macd_df = _compute_macd(df["Close"])
        df = pd.concat([df, macd_df], axis=1)

        df["ADX"] = _compute_adx(df)
        df["CCI"] = _compute_cci(df)
        df["Stoch_%K"], df["Stoch_%D"] = _compute_stochastic(df)
        df["Williams_%R"] = _compute_williams_r(df)
        df["OBV"] = _compute_obv(df)
        df["CMF"] = _compute_cmf(df)
        df["MFI"] = _compute_mfi(df)
        df["VWAP"] = _compute_vwap(df)
        df["VWAP_Deviation"] = df["Close"] - df["VWAP"]
        df["BB_Width"] = _compute_bollinger_width(df["Close"])
        df["BB_Position"] = _compute_bollinger_position(df["Close"])
        df["Volatility_Regime"] = _compute_volatility_regime(df)
        df["Trend_Regime"] = _compute_trend_regime(df)
        df["Liquidity_Regime"] = _compute_liquidity_regime(df)
        df["Market_Stress"] = _compute_market_stress(df)
        df["Composite_Regime_Score"] = _compute_composite_regime_score(df)

        feature_cols.extend(["ADX", "CCI", "Stoch_%K", "Stoch_%D", "Williams_%R", "OBV", "CMF",
                             "MFI", "VWAP_Deviation", "BB_Width", "BB_Position", "MACD", "MACD_Signal",
                             "MACD_Hist", "Volatility_Regime", "Trend_Regime", "Liquidity_Regime",
                             "Market_Stress", "Composite_Regime_Score"])
        # Robust vols
        df["GK_Vol"] = _compute_garman_klass_volatility(df)
        df["Parkinson_Vol"] = _compute_parkinson_volatility(df)
        feature_cols += ["GK_Vol", "Parkinson_Vol"]

        # Advanced (optional: slower)
            # Complexity / entropy
        df["Hurst"] = _compute_hurst_exponent(df["Close"])
        df["Fractal_Dimension"] = _compute_fractal_dimension_from_hurst(df["Close"])
        df["Katz_FD"] = _compute_katz_fractal_dimension(df["Close"])
        df["ApEn"] = _compute_approximate_entropy(df["Close"].pct_change().dropna().reindex(df.index).fillna(0))
        df["PermEn"] = _compute_permutation_entropy(df["Close"].pct_change().dropna().reindex(df.index).fillna(0))
        df["Price_Entropy"] = _compute_price_entropy(df["Close"])

        # Spectral / chaos / DFA
        freqs = np.linspace(0.01, 0.25, 30)
        df["LombScargle"] = _compute_lomb_scargle_power(df["Close"].pct_change().fillna(0), freqs=freqs)
        df["Bispec_Entropy"] = _compute_bispectrum_entropy(df["Close"].pct_change().fillna(0))
        df["Lyapunov"] = _compute_lyapunov_exponent(df["Close"].pct_change().fillna(0))
        df["DFA_alpha"] = _compute_dfa_scaling_exponent(df["Close"].pct_change().fillna(0))
        df["MF_DFA_Hq"] = _compute_multifractal_dfa(df["Close"].pct_change().fillna(0))
        df["Renyi_Entropy"] = _compute_renyi_entropy(df["Close"].pct_change().fillna(0))
        feature_cols += [
            "Hurst", "Fractal_Dimension", "Katz_FD", "ApEn", "PermEn",
            "Price_Entropy", "LombScargle", "Bispec_Entropy", "Lyapunov",
            "DFA_alpha", "MF_DFA_Hq", "Renyi_Entropy"
        ]

        # Dynamics
        df["Velocity_5"] = _compute_price_velocity(df["Close"], 5)
        df["Acceleration_5"] = _compute_price_acceleration(df["Close"], 5)
        df["AbsChange_1"] = _compute_absolute_price_change(df["Close"], 1)
        df["Coppock"] = _compute_coppock_curve(df["Close"])
        feature_cols += ["Velocity_5", "Acceleration_5", "AbsChange_1", "Coppock"]

        # Econometrics
        if self.benchmark is not None:
            aligned_bench = self.benchmark.reindex(df.index)
            df["Beta"] = _compute_rolling_beta(df, aligned_bench)
            df["Alpha"] = _compute_rolling_alpha(df, aligned_bench)
            feature_cols += ["Beta", "Alpha"]

        # GARCH on returns
        ret = df["Close"].pct_change().fillna(0)
        df["GARCH_Vol"] = _compute_garch_volatility(ret)
        feature_cols += ["GARCH_Vol"]


        close = df["Close"]

        # Rolling KL divergence: compare recent window vs previous window (returns)
        df[f"KL_divergence_win30"] = _compute_rolling_kl_divergence(close, window=30, bins=32)
        df[f"KL_divergence_win60"] = _compute_rolling_kl_divergence(close, window=60, bins=32)

        counterpart = None
        if self.benchmark is not None:
            counterpart = self.benchmark.reindex(df.index).fillna(method="ffill")
        else:
            # fallback: use volume (converted to float and normalized)
            counterpart = df["Volume"].astype(float).fillna(0.0)
        series_a = close.pct_change().fillna(0)
        series_b = counterpart.pct_change().fillna(0)
        df[f"Largest_Lagged_Corr_win120_lag10"] = _compute_rolling_largest_lagged_correlation(
            series_a, series_b, window=120, max_lag=10
        )

        # Rolling cross-sample entropy — measures synchrony between asset returns and counterpart
        df[f"CrossSampEn_m2_w120"] = _compute_rolling_cross_sample_entropy(
            series_a, series_b, m=2, r_factor=0.2, window=120
        )


        feature_cols += ["KL_divergence_win30", "KL_divergence_win60"]


        df = self.compute_feature_changes_and_zscores(df, feature_cols= feature_cols,
                                                      lookbacks=[1, 3, 5, 10, 20, 40, 60, 120, 252],
                                                      zscore_window=60)
        self.cache[key] = df
        return df

    def price_action_transformations(self, df, start_date, features, date_columnn_name= "Datetime"):
        """
                Apply transformations to produce price action and statistical features for modeling.

                This method:
                - Filters data to start from `start_date`
                - Generates shifted close values for gap calculation
                - Computes rolling volume averages
                - Extracts calendar features
                - Computes custom metrics like gap %, volatility, Calmar ratio, Sharpe ratio, and various Z-scores.

                Parameters
                ----------
                df : pd.DataFrame
                    Input OHLCV data with a date column and 'Close' column for price-based calcs.
                start_date : str or datetime
                    First date to include in the output DataFrame.
                features : list of str
                    List of additional feature names to compute (in addition to the built-in FEATURES list).
                date_columnn_name : str, default "Datetime"
                    Column name containing date/time values.

                Returns
                -------
                pd.DataFrame
                    Transformed DataFrame containing the original data plus computed features.

                Notes
                -----
                - Gap is computed as `(Open - previous day's close) / previous day's close * 100`.
                - Rolling volatility is computed as the std deviation of returns over the given window.
                - Calmar ratio is `(Return over window) / (Max drawdown over window)`.
                - Sharpe ratio is `(mean return) / (std deviation of return)`.
                - Z-scores normalize changes relative to recent history for comparability.
        """
        df[date_columnn_name] = pd.to_datetime(df[date_columnn_name]).dt.tz_localize(None)
        df = df[df[date_columnn_name] >= start_date].copy()
        df["1D_Shifted_Close"] = df["Close"]
        df["Close"] = df["Close"].shift(periods=-1)

        df["Shifted_Volume"] = df["Volume"].shift(periods=1)
        df["Avg_Rolling_Volume"] = df["Volume"].ewm(span=10, min_periods=0, adjust=False).mean()
        df["Bar_index"] = df.index.values
        df["Date"] = df[date_columnn_name].dt.strftime("%Y-%m-%d")
        df["Month_Year"] = df[date_columnn_name].apply(lambda x: f"{calendar.month_name[int(x.month)]} {x.year}")
        df["Year"] = df[date_columnn_name].dt.year
        df["Day"] = df[date_columnn_name].dt.day
        df["Time"] = df[date_columnn_name].dt.time
        df["Gap"] = (df["Open"] - df["1D_Shifted_Close"]) * 100 / df["1D_Shifted_Close"]
        features = self.FEATURES + features
        features = list(dict.fromkeys(features))  # Remove duplicates

        for feature in features:
            window = None
            if "D" in feature and feature.split("D")[0].isdigit():
                window = int(feature.split("D")[0])

            if "Close_pct_change" in feature and window:
                df[feature] = df["Close"].pct_change(window)

            # Volume % change
            elif "Volume_pct_change" in feature and window:
                df[feature] = df["Volume"].pct_change(window)

            # Rolling volatility (std dev of returns)
            elif re.search(r"\d+D_Vol$", feature) and window:
                df[feature] = df["Close"].pct_change().rolling(window).std()

            # Calmar ratio = (Return over window) / (Max drawdown over window)
            elif "Calmar" in feature and window:
                rolling_return = df["Close"].pct_change(window)
                rolling_max = df["Close"].rolling(window).max()
                drawdown = (df["Close"] - rolling_max) / rolling_max
                max_dd = drawdown.rolling(window).min().abs()
                df[feature] = rolling_return / max_dd.replace(0, np.nan)

            # Sharpe ratio = mean(return) / std(return) over window
            elif "Sharpe" in feature and window:
                ret = df["Close"].pct_change()
                rolling_mean = ret.rolling(window).mean()
                rolling_std = ret.rolling(window).std()
                df[feature] = rolling_mean / rolling_std.replace(0, np.nan)

            # Close Z-score pct change over lookback
            elif "Close_Z_Score_pct_change" in feature and window:
                close_pct_change = df["Close"].pct_change(window)
                lookback = int(feature.split("_")[-2].replace("D", ""))
                rolling_mean = close_pct_change.rolling(lookback).mean()
                rolling_std = close_pct_change.rolling(lookback).std()
                z_score = (close_pct_change - rolling_mean) / rolling_std.replace(0, np.nan)
                df[feature] = z_score


            # Volume Z-score pct change over lookback
            elif "Volume_Z_Score_pct_change" in feature and window:
                volume_pct_change = df["Volume"].pct_change(window)
                lookback = int(feature.split("_")[-2].replace("D", ""))
                rolling_mean = volume_pct_change.rolling(lookback).mean()
                rolling_std = volume_pct_change.rolling(lookback).std()
                z_score = (volume_pct_change - rolling_mean) / rolling_std.replace(0, np.nan)
                df[feature] = z_score

            # Close × Volume Z-score
            elif "Close_x_Volume_Z_Score" in feature and window:
                close_pct_change = df["Close"].pct_change(window)
                volume_pct_change = df["Volume"].pct_change(window)
                close_x_volume = close_pct_change * volume_pct_change
                lookback = int(feature.split("_")[-2].replace("D", ""))
                rolling_mean = close_x_volume.rolling(lookback).mean()
                rolling_std = close_x_volume.rolling(lookback).std()
                z_score = (close_x_volume - rolling_mean) / rolling_std.replace(0, np.nan)
                df[feature] = z_score

            # Volatility Z-score % change
            elif "Volatility_pct_change_Z_Score" in feature and window:
                vol = df["Close"].pct_change().rolling(window).std().pct_change(window)
                lookback = int(feature.split("_")[-2].replace("D", ""))
                rolling_mean = vol.rolling(lookback).mean()
                rolling_std = vol.rolling(lookback).std()
                z_score = (vol - rolling_mean) / rolling_std.replace(0, np.nan)
                df[feature] = z_score

            # Sharpe ratio Z-score % change
            elif "SR_pct_change_Z_Score" in feature and window:
                ret = df["Close"].pct_change()
                sr = (ret.rolling(window).mean() / ret.rolling(window).std()).pct_change(window)
                lookback = int(feature.split("_")[-2].replace("D", ""))
                rolling_mean = sr.rolling(lookback).mean()
                rolling_std = sr.rolling(lookback).std()
                z_score = (sr - rolling_mean) / rolling_std.replace(0, np.nan)
                df[feature] = z_score

            # Calmar ratio Z-score % change
            elif "CR_pct_change_Z_Score" in feature and window:
                rolling_return = df["Close"].pct_change(window)
                rolling_max = df["Close"].rolling(window).max()
                drawdown = (df["Close"] - rolling_max) / rolling_max
                max_dd = drawdown.rolling(window).min().abs()
                cr = (rolling_return / max_dd.replace(0, np.nan)).pct_change(window)
                lookback = int(feature.split("_")[-2].replace("D", ""))
                rolling_mean = cr.rolling(lookback).mean()
                rolling_std = cr.rolling(lookback).std()
                z_score = (cr - rolling_mean) / rolling_std.replace(0, np.nan)
                df[feature] = z_score.pct_change()

        # df = df.dropna().reset_index(drop=True)
        missing_percentage = df.isnull().mean()
        cols_to_drop = missing_percentage[missing_percentage > 0.5].index
        df = df.drop(columns=cols_to_drop)
        return df

    def compute_feature_changes_and_zscores(self, df, feature_cols,
                                            lookbacks=None, zscore_window=60):
        """
        Compute percentage changes over multiple lookback periods and their rolling Z-scores
        for all technical indicator feature columns.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame containing computed technical indicator features (output of compute_features).
        lookbacks : list of int, optional
            List of lookback periods (in trading days) over which to compute percentage changes.
            Default: [1, 3, 5, 10, 20, 40, 60, 120, 252]
        zscore_window : int, optional
            Rolling window size (in days) for computing Z-scores of percentage changes.
            Default: 60

        Returns
        -------
        pd.DataFrame
            Original DataFrame with additional columns:
            - `{feature}_pctchg_{N}D` for each lookback N
            - `{feature}_pctchg_{N}D_zscore` for the rolling Z-score of each pct change column.

        Notes
        -----
        - Percentage change is computed as: `(current_value / value_N_days_ago - 1) * 100`.
        - Z-score is computed as: `(x - rolling_mean) / rolling_std`.
        - The function skips columns that are not numeric.
        - NaNs will be present at the start of each lookback window and at the start of the Z-score window.
        """

        if lookbacks is None:
            lookbacks = [1, 3, 5, 10, 20, 40, 60, 120, 252]

        df = df.copy()

        # Identify only numeric feature columns (exclude date, ticker, etc.)

        for col in feature_cols:
            for lb in lookbacks:
                pct_col = f"{col}_pct_change_{lb}D"
                z_col = f"{pct_col}_Z_Score_{zscore_window}_lookback"

                # Percentage change
                df[pct_col] = df[col].pct_change(lb) * 100

                # Rolling Z-score
                rolling_mean = df[pct_col].rolling(zscore_window).mean()
                rolling_std = df[pct_col].rolling(zscore_window).std()
                df[z_col] = (df[pct_col] - rolling_mean) / rolling_std

        return df

    def compute_cross_sectional_features(self, df_all, datetime_column_name= "Datetime",
                                         rank_method="dense"):
        """
        Compute cross-sectional features across multiple tickers using precomputed per-ticker data.

        Parameters
        ----------
        df_all : pd.DataFrame
            Combined dataframe of all the tickers in the universe.
        rank_method : {"average", "min", "max", "dense", "first"}, optional (default="dense")
            Method to handle ties in ranking. See `pandas.DataFrame.rank`.

        Returns
        -------
        pd.DataFrame
            Multi-index DataFrame with (Ticker, Date) index, containing:
            - Original features from each ticker.
            - Cross-sectional ranks for each specified return period.
            - Cross-sectional z-scores for each return period.
        """


        zscore_cols = [col for col in df_all.columns if "Z_Score" in col]
        for col in zscore_cols:
            rank_name = f"{col}_Cross_Sectional_Rank"
            df_all[rank_name] = df_all.groupby(datetime_column_name)[col].rank(method=rank_method,
                                                                                     ascending=False)

        # Step 3: Auto-detect pct_change columns and rank them cross-sectionally
        pct_cols = [col for col in df_all.columns if "pct_change" in col]
        for col in pct_cols:
            rank_name = f"{col}_Cross_Sectional_Rank"
            df_all[rank_name] = df_all.groupby(datetime_column_name)[col].rank(method=rank_method,
                                                                                     ascending=False)
        spread_cols = [col for col in df_all.columns if "Spread" in col]
        for col in spread_cols:
            rank_name = f"{col}_Cross_Sectional_Rank"
            df_all[rank_name] = df_all.groupby(datetime_column_name)[col].rank(method=rank_method,
                                                                                     ascending=False)
        return df_all

    def compute_sector_spreads(self, data, mapping_df,
                               ticker_column_name, datetime_column_name,
                               sector_column_name, returns_column_name, windows=None):
        """
               Compute sector-relative spreads in returns and volatilities across multiple horizons.

        This method calculates the spread between each company's returns/volatilities
        and the median return/volatility of its respective sector. It supports multiple
        rolling horizons, enabling cross-sectional analysis of sector-relative performance.

        Workflow:
        1. Load a company-to-sector mapping file.
        2. Compute or load daily median sector returns from company-level returns.
        3. Merge sector information into the company-level dataset.
        4. For each rolling horizon (e.g., 1, 3, 5, 10, 20, 40, 60, 120, 252 days):
            - Compute company cumulative return vs. sector cumulative return.
            - Compute company rolling volatility vs. sector rolling volatility.
            - Derive spreads:
                * Return_Spread_{window}D = Company cumulative return - Sector cumulative return
                * Vol_Spread_{window}D    = Company rolling volatility - Sector rolling volatility

        Parameters
        ----------
        data : pd.DataFrame
            Company-level returns data. Must contain at least:
            - ticker_column_name
            - datetime_column_name
            - returns_column_name


        mapping_df: str
            Path to a CSV file mapping companies to their respective sectors.
            Must contain: ['Symbol', 'Sector'] (column names are case-insensitive).

        ticker_column_name : str
            Column name in `data` and `mapping_file` identifying company tickers.

        datetime_column_name : str
            Column name in `data` representing trading dates.

        sector_column_name : str
            Column name in `mapping_file` identifying sector membership.

        returns_column_name : str
            Column name in `data` representing daily returns of companies.

        windows : list of int, optional
            Rolling horizons (in trading days) over which spreads are computed.
            Default: [1, 3, 5, 10, 20, 40, 60, 120, 252].

        Returns
        -------
        pd.DataFrame
            Extended DataFrame containing:
            - Original company-level columns
            - 'Sector' and 'Sector_Return'
            - For each window in `windows`:
                * Company_CumRet_{w}D
                * Sector_CumRet_{w}D
                * Return_Spread_{w}D
                * Company_Vol_{w}D
                * Sector_Vol_{w}D
                * Vol_Spread_{w}D

        Notes
        -----
        - Cumulative returns are computed as the rolling sum of daily returns.
          For short horizons (1–5 days), this is a close approximation to compounded returns.
        - Volatilities are computed as rolling standard deviations of daily returns.
        - The function internally calls `_compute_daily_sector_median_returns` to ensure
          sector median returns are consistent with the provided company return data.
        - Input column names are normalized to Title Case internally for consistency.
        """
        if windows is None:
            windows = [1, 3, 5, 10, 20, 40, 60, 120, 252]

        # Load mapping + sector returns
        df = data
        sector_df = _compute_daily_sector_median_returns(mapping_df, df,
                                                         ticker_column_name = ticker_column_name,
                                                         datetime_column_name = datetime_column_name,
                                                         sector_column_name = sector_column_name,
                                                         returns_column_name = returns_column_name,
                                             output_file=None)

        # Normalize column names

        # Merge mapping
        df = df.merge(mapping_df, on=ticker_column_name, how="left")

        # Merge sector returns
        df = df.merge(sector_df, on=[datetime_column_name, sector_column_name], how="left")

        # Rename for clarity
        df = df.rename(columns={"Median_return": "Sector_Return"})

        # Sort for rolling ops
        df = df.sort_values([ticker_column_name, datetime_column_name])
        # ---- RETURN SPREADS ----

        for w in windows:
            # Cumulative returns over horizon w
            df[f"Company_CumRet_{w}D"] = (
                    1 + df.groupby(ticker_column_name)[returns_column_name].transform(lambda x: x.rolling(w).sum())
            )
            df[f"Sector_CumRet_{w}D"] = (
                    1 + df.groupby(sector_column_name)["Median_Return"].transform(lambda x: x.rolling(w).sum())
            )
            df[f"Return_Spread_{w}D"] = df[f"Company_CumRet_{w}D"] - df[f"Sector_CumRet_{w}D"]
            df[f"Return_Spread_{w}D_pct_change"] = df[f"Return_Spread_{w}D"].pct_change()

        # ---- VOLATILITY SPREADS ----
        for w in windows:
            df[f"Company_Vol_{w}D"] = (
                df.groupby(ticker_column_name)[returns_column_name].transform(lambda x: x.rolling(w).std())
            )
            df[f"Sector_Vol_{w}D"] = (
                df.groupby(sector_column_name)["Median_Return"].transform(lambda x: x.rolling(w).std())
            )
            df[f"Vol_Spread_{w}D"] = df[f"Company_Vol_{w}D"] - df[f"Sector_Vol_{w}D"]
            df[f"Vol_Spread_{w}D_pct_change"] = df[f"Vol_Spread_{w}D"].pct_change()


        return df
