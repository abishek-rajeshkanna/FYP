import os

# Disable rendering for faster training execution
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
pygame.init()
pygame.display.set_mode((1, 1))

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv

from drl2.env_emv import EMVEnvironment
from drl2.config import EPISODES, STEPS_PER_EPISODE


MODEL_NAME = "models/mcars"


def make_env():
    return EMVEnvironment()


def train():

    print("=================================")
    print("DRL2 TRAINING STARTED")
    print("=================================")

    # Vectorized environment for stable training
    env = DummyVecEnv([make_env])

    total_steps = EPISODES * STEPS_PER_EPISODE
    print("Total training steps:", total_steps)

    # PPO model configuration
    model = PPO(
        policy="MlpPolicy",
        env=env,
        verbose=1,
        learning_rate=3e-4,
        gamma=0.99,
        n_steps=256,
        batch_size=64,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.01,
        vf_coef=0.5,
        tensorboard_log="./ppo_tensorboard/"
    )

    # Training phase
    model.learn(total_timesteps=total_steps)

    # Save trained model
    os.makedirs("models", exist_ok=True)
    model.save(MODEL_NAME)

    print("=================================")
    print("TRAINING FINISHED")
    print("Model saved →", MODEL_NAME + ".zip")
    print("=================================")


if __name__ == "__main__":
    train()