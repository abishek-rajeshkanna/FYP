# rl/traffic_env.py

import numpy as np

from env.simulation import Simulation
from rl.state_encoder import StateEncoder
from rl.reward import RewardCalculator


class TrafficEnv:

    def __init__(self, width=1024, height=768):

        # simulator (HEADLESS TRAINING MODE)
        self.simulation = Simulation(width, height, render=False)

        # helpers
        self.encoder = StateEncoder()
        self.reward_calc = RewardCalculator()

        self.prev_lane_stats = None

        # reduce steps for faster training
        self.max_steps = 200
        self.current_step = 0

    # ------------------------------------------------

    def reset(self):

        # recreate simulation (keep render disabled)
        self.simulation = Simulation(
            self.simulation.width,
            self.simulation.height,
            render=False
        )

        self.current_step = 0

        lane_stats = self.simulation.get_lane_statistics()
        ev_data = self.simulation.detect_ev_lanes()

        self.prev_lane_stats = lane_stats

        state = self.encoder.encode(
            lane_stats,
            ev_data,
            self.simulation.signal
        )

        return np.array(state, dtype=np.float32)

    # ------------------------------------------------

    def step(self, action):

        self.current_step += 1

        # Apply action to signal
        if action == 1:
            self.simulation.signal.switch_phase()

        elif action == 2:
            self.simulation.signal.extend_green()

        # Run simulator step
        self.simulation.update()

        # Collect new state
        lane_stats = self.simulation.get_lane_statistics()
        ev_data = self.simulation.detect_ev_lanes()

        next_state = self.encoder.encode(
            lane_stats,
            ev_data,
            self.simulation.signal
        )

        # Compute reward
        reward = self.reward_calc.compute_reward(
            self.prev_lane_stats,
            lane_stats,
            ev_data
        )

        self.prev_lane_stats = lane_stats

        # End episode
        done = False

        if self.current_step >= self.max_steps:
            done = True

        return (
            np.array(next_state, dtype=np.float32),
            reward,
            done,
            {}
        )

    # ------------------------------------------------

    def render(self, screen):

        self.simulation.draw(screen)