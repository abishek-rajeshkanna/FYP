import numpy as np
import os
import torch

from rl.traffic_env import TrafficEnv
from rl.marl_agent import MARLAgent


class Trainer:

    def __init__(self):

        self.env = TrafficEnv()

        self.state_size = 14   # updated after state encoder changes
        self.action_size = 3

        # shared multi-agent policy
        self.agent = MARLAgent(self.state_size, self.action_size)

        self.num_agents = 4   # 4 signals

    # ------------------------------------------------

    def train(self, episodes=10):

        print("Starting training...")

        for episode in range(episodes):

            state = self.env.reset()

            total_reward = 0
            done = False

            # storage for PPO update
            states = []
            actions = []
            log_probs = []
            rewards = []

            while not done:

                agent_actions = []
                agent_log_probs = []

                # each signal agent acts independently
                for _ in range(self.num_agents):

                    action, log_prob = self.agent.act(state)

                    agent_actions.append(action)
                    agent_log_probs.append(log_prob)

                # coordination across signals (consensus-based)
                action = max(set(agent_actions), key=agent_actions.count)

                next_state, reward, done, _ = self.env.step(action)

                # store experience
                states.append(state)
                actions.append(action)
                log_probs.append(agent_log_probs[0])
                rewards.append(reward)

                state = next_state
                total_reward += reward

            # ------------------------------------------------
            # POLICY UPDATE (CENTRALIZED TRAINING)
            # ------------------------------------------------

            self.agent.train(states, actions, log_probs, rewards)

            print(f"Episode {episode}  Reward: {total_reward}")

        # ------------------------------------------------
        # SAVE MODEL
        # ------------------------------------------------

        os.makedirs("models", exist_ok=True)

        self.agent.save("models/signal_mappo.pth")

        print("\nTraining finished.")
        print("Model saved to: models/signal_mappo.pth")