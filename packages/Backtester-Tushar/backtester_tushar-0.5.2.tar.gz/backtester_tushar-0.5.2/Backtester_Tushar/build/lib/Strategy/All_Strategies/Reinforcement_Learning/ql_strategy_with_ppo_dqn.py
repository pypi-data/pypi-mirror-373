import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import torch
import torch.nn as nn
import torch.optim as optim
import random
from collections import deque
from Backtester_Tushar.Strategy.ml_base_class import MLStrategy


class QLStrategy(MLStrategy):
    """Implements an RL-based trading strategy with PPO or DQN."""

    def __init__(self, timeframe="daily", atr_period=14, state_size=10, action_space=[0, 1, -1],
                 rl_algorithm="dqn", learning_rate=0.001, discount_factor=0.95, max_steps=100,
                 hidden_size=64, replay_buffer_size=10000, batch_size=64, target_update_freq=100, feature_configs=None,
                 base_risk=150000, atr_threshold=5):
        super().__init__("QLStrategy", timeframe, atr_period, feature_configs, base_risk, atr_threshold)
        self.state_size = state_size
        self.action_space = action_space
        self.rl_algorithm = rl_algorithm.lower()
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.max_steps = max_steps
        self.hidden_size = hidden_size
        self.replay_buffer_size = replay_buffer_size
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq
        self.features = ["Close", "Volume", "ATR_percent", "PE_Ratio", "EPS_Growth_4", "Debt_to_Equity",
                         "Social_Media_Sentiment", "Macro_Indicator"] + \
                        [f"{w}_Volatility" for w in [1, 10, 22]] + \
                        [col for col in feature_configs if col["name"] in ["RSI", "Momentum"]] + \
                        [f"BB_upper_{config['params']['period']}" for config in feature_configs if
                         config["name"] == "Bollinger_Bands"] + \
                        [f"BB_lower_{config['params']['period']}" for config in feature_configs if
                         config["name"] == "Bollinger_Bands"]
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.scaler = StandardScaler()
        self.epsilon = 0.1

        if self.rl_algorithm == "ppo":
            self.policy_net = self._build_ppo_model().to(self.device)
            self.value_net = self._build_value_model().to(self.device)
            self.policy_optimizer = optim.Adam(self.policy_net.parameters(), lr=self.learning_rate)
            self.value_optimizer = optim.Adam(self.value_net.parameters(), lr=self.learning_rate)
        else:
            self.q_net = self._build_dqn_model().to(self.device)
            self.target_net = self._build_dqn_model().to(self.device)
            self.target_net.load_state_dict(self.q_net.state_dict())
            self.optimizer = optim.Adam(self.q_net.parameters(), lr=self.learning_rate)
            self.replay_buffer = deque(maxlen=replay_buffer_size)
            self.step_count = 0

    def risk_allocation(self, row):
        base_risk = self.base_risk_allocation(row)
        if pd.isna(base_risk):
            return np.nan
        state = row[self.features][:self.state_size].values
        state_tensor = torch.tensor([state], dtype=torch.float32).to(self.device)
        if self.rl_algorithm == "ppo":
            with torch.no_grad():
                probs = self.policy_net(state_tensor)
                confidence = probs.max().item()
            return base_risk * (1.33 if confidence > 0.7 else 1.0)
        else:
            with torch.no_grad():
                q_values = self.q_net(state_tensor)
                confidence = q_values.max().item()
            return base_risk * (1.33 if confidence > 0.5 else 1.0)

    def _build_ppo_model(self):
        class PolicyNetwork(nn.Module):
            def __init__(self, state_size, action_size, hidden_size):
                super(PolicyNetwork, self).__init__()
                self.fc1 = nn.Linear(state_size, hidden_size)
                self.fc2 = nn.Linear(hidden_size, hidden_size)
                self.fc3 = nn.Linear(hidden_size, action_size)
                self.softmax = nn.Softmax(dim=-1)

            def forward(self, x):
                x = torch.relu(self.fc1(x))
                x = torch.relu(self.fc2(x))
                x = self.fc3(x)
                return self.softmax(x)

        return PolicyNetwork(self.state_size, len(self.action_space), self.hidden_size)

    def _build_value_model(self):
        class ValueNetwork(nn.Module):
            def __init__(self, state_size, hidden_size):
                super(ValueNetwork, self).__init__()
                self.fc1 = nn.Linear(state_size, hidden_size)
                self.fc2 = nn.Linear(hidden_size, hidden_size)
                self.fc3 = nn.Linear(hidden_size, 1)

            def forward(self, x):
                x = torch.relu(self.fc1(x))
                x = torch.relu(self.fc2(x))
                return self.fc3(x)

        return ValueNetwork(self.state_size, self.hidden_size)

    def _build_dqn_model(self):
        class QNetwork(nn.Module):
            def __init__(self, state_size, action_size, hidden_size):
                super(QNetwork, self).__init__()
                self.fc1 = nn.Linear(state_size, hidden_size)
                self.fc2 = nn.Linear(hidden_size, hidden_size)
                self.fc3 = nn.Linear(hidden_size, action_size)

            def forward(self, x):
                x = torch.relu(self.fc1(x))
                x = torch.relu(self.fc2(x))
                return self.fc3(x)

        return QNetwork(self.state_size, len(self.action_space), self.hidden_size)

    def train_model(self, df):
        if len(df) < 2:
            return

        df = df.copy()
        X = df[self.features].dropna()
        X_scaled = self.scaler.fit_transform(X)
        df[self.features] = pd.DataFrame(X_scaled, index=X.index, columns=self.features)
        env = TradingEnvironment(df, self.features, self.action_space, self.max_steps)

        if self.rl_algorithm == "ppo":
            self._train_ppo(env)
        else:
            self._train_dqn(env)

    def _train_ppo(self, env, episodes=10, clip_epsilon=0.2, gae_lambda=0.95):
        for _ in range(episodes):
            state = env.reset()
            states, actions, rewards, log_probs, values = [], [], [], [], []
            done = False

            while not done:
                state_tensor = torch.tensor([state], dtype=torch.float32).to(self.device)
                with torch.no_grad():
                    probs = self.policy_net(state_tensor)
                    value = self.value_net(state_tensor)
                    dist = torch.distributions.Categorical(probs)
                    action_idx = dist.sample()
                    log_prob = dist.log_prob(action_idx)

                action = self.action_space[action_idx.item()]
                next_state, reward, done = env.step(action)

                states.append(state)
                actions.append(action_idx)
                rewards.append(reward)
                log_probs.append(log_prob)
                values.append(value)

                state = next_state

            returns = []
            advantages = []
            discounted_sum = 0
            for r in rewards[::-1]:
                discounted_sum = r + self.discount_factor * discounted_sum
                returns.insert(0, discounted_sum)

            returns = torch.tensor(returns, dtype=torch.float32).to(self.device)
            values = torch.cat(values).squeeze()
            advantages = returns - values
            advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

            states_tensor = torch.tensor(states, dtype=torch.float32).to(self.device)
            actions_tensor = torch.tensor(actions, dtype=torch.long).to(self.device)
            old_log_probs = torch.cat(log_probs)

            for _ in range(5):
                probs = self.policy_net(states_tensor)
                dist = torch.distributions.Categorical(probs)
                new_log_probs = dist.log_prob(actions_tensor)
                ratios = torch.exp(new_log_probs - old_log_probs)
                surr1 = ratios * advantages
                surr2 = torch.clamp(ratios, 1 - clip_epsilon, 1 + clip_epsilon) * advantages
                policy_loss = -torch.min(surr1, surr2).mean()

                value_pred = self.value_net(states_tensor).squeeze()
                value_loss = ((value_pred - returns) ** 2).mean()

                self.policy_optimizer.zero_grad()
                policy_loss.backward()
                self.policy_optimizer.step()

                self.value_optimizer.zero_grad()
                value_loss.backward()
                self.value_optimizer.step()

    def _train_dqn(self, env, episodes=5):  # reduced for performance
        for _ in range(episodes):
            state = env.reset()
            done = False

            while not done:
                if random.random() < self.epsilon:
                    action_idx = random.randint(0, len(self.action_space) - 1)
                else:
                    state_tensor = torch.tensor([state], dtype=torch.float32).to(self.device)
                    with torch.no_grad():
                        q_vals = self.q_net(state_tensor)
                        action_idx = q_vals.argmax().item()

                action = self.action_space[action_idx]
                next_state, reward, done = env.step(action)
                self.replay_buffer.append((state, action_idx, reward, next_state, done))
                state = next_state

                if len(self.replay_buffer) < self.batch_size:
                    continue

                batch = random.sample(self.replay_buffer, self.batch_size)
                states, actions, rewards, next_states, dones = zip(*batch)

                states = torch.tensor(states, dtype=torch.float32).to(self.device)
                actions = torch.tensor(actions, dtype=torch.long).to(self.device)
                rewards = torch.tensor(rewards, dtype=torch.float32).to(self.device)
                next_states = torch.tensor(next_states, dtype=torch.float32).to(self.device)
                dones = torch.tensor(dones, dtype=torch.float32).to(self.device)

                q_vals = self.q_net(states).gather(1, actions.unsqueeze(1)).squeeze()
                with torch.no_grad():
                    next_q = self.target_net(next_states).max(1)[0]
                    targets = rewards + self.discount_factor * next_q * (1 - dones)

                loss = nn.MSELoss()(q_vals, targets)
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()

                self.step_count += 1
                if self.step_count % self.target_update_freq == 0:
                    self.target_net.load_state_dict(self.q_net.state_dict())

        self.epsilon = max(0.01, self.epsilon * 0.99)

    def predict(self, df):
        df = df.copy()
        X = df[self.features].dropna()
        X_scaled = self.scaler.transform(X)
        df[self.features] = pd.DataFrame(X_scaled, index=X.index, columns=self.features)
        predictions = []

        for i, row in df.iterrows():
            state = row[self.features][:self.state_size].values
            state_tensor = torch.tensor([state], dtype=torch.float32).to(self.device)

            if self.rl_algorithm == "ppo":
                with torch.no_grad():
                    probs = self.policy_net(state_tensor)
                    action_idx = torch.distributions.Categorical(probs).sample().item()
            else:
                with torch.no_grad():
                    q_values = self.q_net(state_tensor)
                    action_idx = q_values.argmax().item()

            action = self.action_space[action_idx]
            predictions.append(action)

        return pd.Series(predictions, index=df.index)
