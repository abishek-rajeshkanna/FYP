import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from stable_baselines3 import PPO


class Actor(nn.Module):

    def __init__(self, state_dim, action_dim):

        super(Actor, self).__init__()

        self.net = nn.Sequential(
            nn.Linear(state_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, action_dim),
            nn.Softmax(dim=-1)
        )

    def forward(self, x):
        return self.net(x)


class Critic(nn.Module):

    def __init__(self, state_dim):

        super(Critic, self).__init__()

        self.net = nn.Sequential(
            nn.Linear(state_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )

    def forward(self, x):
        return self.net(x)


class CustomPPO:

    def __init__(self, state_dim, action_dim, lr=3e-4, gamma=0.99, eps_clip=0.2):

        self.actor = Actor(state_dim, action_dim)
        self.critic = Critic(state_dim)

        self.optimizer = optim.Adam(
            list(self.actor.parameters()) + list(self.critic.parameters()),
            lr=lr
        )

        self.gamma = gamma
        self.eps_clip = eps_clip

    def select_action(self, state):

        state = torch.FloatTensor(state)

        probs = self.actor(state)
        dist = torch.distributions.Categorical(probs)

        action = dist.sample()

        return action.item(), dist.log_prob(action)

    def compute_returns(self, rewards):

        returns = []
        G = 0

        for r in reversed(rewards):
            G = r + self.gamma * G
            returns.insert(0, G)

        return torch.tensor(returns, dtype=torch.float32)

    def update(self, states, actions, old_log_probs, rewards):

        states = torch.FloatTensor(states)
        actions = torch.LongTensor(actions)
        old_log_probs = torch.stack(old_log_probs)

        returns = self.compute_returns(rewards)
        values = self.critic(states).squeeze()

        advantages = returns - values.detach()

        probs = self.actor(states)
        dist = torch.distributions.Categorical(probs)

        new_log_probs = dist.log_prob(actions)

        ratio = torch.exp(new_log_probs - old_log_probs)

        surr1 = ratio * advantages
        surr2 = torch.clamp(ratio, 1 - self.eps_clip, 1 + self.eps_clip) * advantages

        actor_loss = -torch.min(surr1, surr2).mean()

        critic_loss = nn.MSELoss()(values, returns)

        loss = actor_loss + 0.5 * critic_loss

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()


class DRLPolicy:

    def __init__(self, model_path="models/mcars.zip"):

        self.use_custom = False

        try:
            self.model = PPO.load(model_path)
            print("DRL model loaded:", model_path)

        except Exception as e:

            print("Model not found, switching to alternative policy")
            print(e)

            self.model = None
            self.use_custom = True

            self.custom_model = CustomPPO(state_dim=10, action_dim=4)

    def act(self, state):

        state = np.array(state, dtype=np.float32)

        if self.model is not None:

            state_input = state.reshape(1, -1)
            action, _ = self.model.predict(state_input, deterministic=True)

            return int(action[0])

        if self.use_custom:

            action, _ = self.custom_model.select_action(state)
            return action

        return np.random.randint(0, 4)