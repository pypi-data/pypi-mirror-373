import numpy as np


class TradingEnvironment:
    """RL environment for trading."""

    def __init__(self, df, features, action_space=[0, 1, -1], max_steps=100):
        self.df = df.reset_index(drop=True)
        self.features = features
        self.action_space = action_space
        self.max_steps = max_steps
        self.current_step = 0
        self.done = False

    def reset(self):
        self.current_step = 0
        self.done = False
        return self._get_state()

    def _get_state(self):
        if self.current_step >= len(self.df):
            self.done = True
            return np.zeros(len(self.features))
        return self.df[self.features].iloc[self.current_step].values

    def step(self, action):
        if self.done or self.current_step >= len(self.df) - 1:
            self.done = True
            return np.zeros(len(self.features)), 0, True

        current_price = self.df["Close"].iloc[self.current_step]
        next_price = self.df["Close"].iloc[self.current_step + 1]
        reward = (next_price - current_price) * action
        self.current_step += 1
        next_state = self._get_state()
        self.done = self.current_step >= self.max_steps or self.current_step >= len(self.df) - 1
        return next_state, reward, self.done
