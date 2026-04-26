import gymnasium as gym
import numpy as np
import random

from drl2.state import StateEncoder
from drl2.reward import RewardFunction
from env.simulation import Simulation


class EMVEnvironment(gym.Env):

    def __init__(self):

        super().__init__()

        self.encoder = StateEncoder()
        self.reward_fn = RewardFunction()

        self.sim = Simulation(1024, 768)

        # Action space: keep, lane change, brake, accelerate
        self.action_space = gym.spaces.Discrete(4)

        # State space (10 features)
        self.observation_space = gym.spaces.Box(
            low=0,
            high=1,
            shape=(10,),
            dtype=np.float32
        )

        self.max_steps = 300
        self.step_count = 0

    # --------------------------------------------------

    def reset(self, seed=None, options=None):

        super().reset(seed=seed)

        self.sim = Simulation(1024, 768)
        self.step_count = 0

        v, c = random.choice(self.sim.vehicles)

        self.agent_vehicle = v
        self.agent_controller = c

        state = self.encoder.encode(
            self.agent_controller,
            self.sim.vehicles
        )

        return state.astype(np.float32), {}

    # --------------------------------------------------

    def step(self, action):

        self.step_count += 1

        prev_x = self.agent_vehicle.x
        prev_y = self.agent_vehicle.y

        ctrl = self.agent_controller

        # --------------------------------
        # APPLY ACTION ON CONTROLLER
        # --------------------------------

        if action == 1:
            # lane change handled internally by controller logic
            pass

        elif action == 2:
            ctrl.current_speed *= 0.7

        elif action == 3:
            ctrl.current_speed = min(
                ctrl.current_speed * 1.3,
                ctrl.desired_speed * 2.0
            )

        # --------------------------------
        # ADVANCE SIMULATION
        # --------------------------------

        self.sim.update()

        # --------------------------------
        # GET STATE
        # --------------------------------

        state = self.encoder.encode(
            self.agent_controller,
            self.sim.vehicles
        )

        # --------------------------------
        # COMPUTE REWARD
        # --------------------------------

        reward = self.reward_fn.compute(
            self.agent_vehicle,
            (prev_x, prev_y),
            action
        )

        terminated = False
        truncated = False

        if self.step_count >= self.max_steps:
            truncated = True

        return state.astype(np.float32), reward, terminated, truncated, {}

    # --------------------------------------------------

    def render(self):
        pass