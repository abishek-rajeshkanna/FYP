import random
from collections import deque


class ReplayBuffer:

    def __init__(self, capacity=10000):

        # maximum memory size
        self.buffer = deque(maxlen=capacity)

    # ------------------------------------------------

    def push(self, state, action, reward, next_state):

        experience = (state, action, reward, next_state)

        self.buffer.append(experience)

    # ------------------------------------------------

    def sample(self, batch_size):

        batch = random.sample(self.buffer, batch_size)

        states = []
        actions = []
        rewards = []
        next_states = []

        for experience in batch:

            state, action, reward, next_state = experience

            states.append(state)
            actions.append(action)
            rewards.append(reward)
            next_states.append(next_state)

        return states, actions, rewards, next_states

    # ------------------------------------------------

    def __len__(self):

        return len(self.buffer)