import hashlib

class FeatureGenerator:
    def __init__(self, feature_configs=None):
        self.feature_configs = feature_configs or []
        self.cache = {}

    def _hash_df(self, df, cols):
        # Use only recent rows to reduce hash size
        concat_str = "".join([str(df[c].values[-20:]) for c in cols if c in df])
        return hashlib.md5((concat_str + str(self.feature_configs)).encode()).hexdigest()

    def compute_features(self, df):
        df = df.copy()
        key = self._hash_df(df, ["Close", "High", "Low", "Volume"])
        if key in self.cache:
            return self.cache[key]

        for config in self.feature_configs:
            name, params = config.get("name"), config.get("params", {})
            if name == "RSI":
                period = params.get("period", 14)
                df[f"RSI_{period}"] = self._compute_rsi(df["Close"], period)
            elif name == "Bollinger_Bands":
                period = params.get("period", 20)
                df[[f"BB_upper_{period}", f"BB_lower_{period}"]] = self._compute_bollinger(df["Close"], period)
            elif name == "Momentum":
                period = params.get("period", 10)
                df[f"Momentum_{period}"] = df["Close"].diff(period)
            elif name == "PE_Ratio" and "PE_Ratio" in df:
                df["PE_Ratio"] = df["PE_Ratio"]
            elif name == "EPS_Growth":
                df[f"EPS_Growth_{params.get('period', 4)}"] = self._compute_eps_growth(df, params.get("period", 4))
            elif name == "Debt_to_Equity" and "Debt_to_Equity" in df:
                df["Debt_to_Equity"] = df["Debt_to_Equity"]
            elif name == "Social_Media_Sentiment":
                df["Social_Media_Sentiment"] = df.get("Social_Media_Sentiment", 0)
            elif name == "Macro_Indicator":
                key = params.get("name", "Macro_Indicator")
                df[f"Macro_Indicator_{key}"] = df.get(key, 0)

        self.cache[key] = df
        return df

    # RSI, Bollinger, EPS growth remain unchanged.
