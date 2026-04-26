import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np


# ------------------------------------------------
# Actor Network (Policy)
# ------------------------------------------------

class Actor(nn.Module):

    def __init__(self, state_size, action_size):

        super(Actor, self).__init__()

        self.net = nn.Sequential(
            nn.Linear(state_size, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, action_size),
            nn.Softmax(dim=-1)
        )

    def forward(self, x):
        return self.net(x)


# ------------------------------------------------
# Critic Network (Centralized Value Function)
# ------------------------------------------------

class Critic(nn.Module):

    def __init__(self, state_size):

        super(Critic, self).__init__()

        self.net = nn.Sequential(
            nn.Linear(state_size, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )

    def forward(self, x):
        return self.net(x)


# ------------------------------------------------
# Multi-Agent PPO (Shared Policy)
# ------------------------------------------------

class MARLAgent:

    def __init__(self, state_size, action_size):

        self.state_size = state_size
        self.action_size = action_size

        self.gamma = 0.99
        self.lr = 3e-4
        self.eps_clip = 0.2

        self.device = torch.device("cpu")

        # Shared policy across all signal agents
        self.actor = Actor(state_size, action_size).to(self.device)

        # Centralized critic
        self.critic = Critic(state_size).to(self.device)

        self.optimizer = optim.Adam(
            list(self.actor.parameters()) + list(self.critic.parameters()),
            lr=self.lr
        )

    # ------------------------------------------------

    def act(self, state):

        state = torch.FloatTensor(state).to(self.device)

        probs = self.actor(state)
        dist = torch.distributions.Categorical(probs)

        action = dist.sample()

        return action.item(), dist.log_prob(action)

    # ------------------------------------------------

    def compute_returns(self, rewards):

        returns = []
        G = 0

        for r in reversed(rewards):
            G = r + self.gamma * G
            returns.insert(0, G)

        return torch.tensor(returns, dtype=torch.float32)

    # ------------------------------------------------

    def train(self, states, actions, old_log_probs, rewards):

        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        old_log_probs = torch.stack(old_log_probs).to(self.device)

        returns = self.compute_returns(rewards).to(self.device)

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

    # ------------------------------------------------

    def save(self, path):

        torch.save({
            "actor": self.actor.state_dict(),
            "critic": self.critic.state_dict()
        }, path)

    # ------------------------------------------------

    def load(self, path):

        checkpoint = torch.load(path, map_location=self.device)

        self.actor.load_state_dict(checkpoint["actor"])
        self.critic.load_state_dict(checkpoint["critic"])