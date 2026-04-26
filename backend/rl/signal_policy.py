import torch
import numpy as np

from rl.marl_agent import MARLAgent


class SignalPolicy:

    def __init__(self, model_path="models/signal_policy.pth"):

        self.state_size = 14
        self.action_size = 3

        self.agent = MARLAgent(self.state_size, self.action_size)

        try:
            self.agent.load(model_path)
            print("Signal MAPPO model loaded:", model_path)

        except Exception as e:
            print("Model not found, using default policy")
            print(e)

    # ------------------------------------------------

    def act(self, state):

        state = torch.FloatTensor(state)

        with torch.no_grad():

            probs = self.agent.actor(state)
            dist = torch.distributions.Categorical(probs)

            action = dist.sample()

        return action.item()