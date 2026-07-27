"""
train.py
--------
This file teaches (trains) a computer AI to land a spaceship safely.
We use a method called PPO (a popular and easy way to train game-playing AI).

HOW TO RUN THIS FILE:
1. Open a terminal in this folder
2. Run: pip install -r requirements-training.txt
3. Run: python train.py
4. Wait for training to finish (this can take 10-30 minutes on a normal laptop)
5. After it finishes, you will see new files inside the "models" and "static" folders

You only need to run this file ONE TIME on your own computer.
You do NOT run this file on Render. Render only shows the results.
"""

import os
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")  # this lets us save graph pictures without opening a window
import matplotlib.pyplot as plt

import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.evaluation import evaluate_policy


# ---------------------------------------------------------
# STEP 1: Make folders where we will save our files
# ---------------------------------------------------------
os.makedirs("models", exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs("logs", exist_ok=True)

MODEL_SAVE_PATH = "models/ppo_lunar_lander.zip"
GRAPH_SAVE_PATH = "static/training_reward_graph.png"
RESULTS_SAVE_PATH = "static/results.json"

# How long we want to train. Bigger number = smarter AI but takes longer.
# Lunar Lander usually needs around 1,000,000 steps before it can land well
# and reach an average score of 200+ (this is normally called "solved").
# On a normal laptop with one CPU, 1,000,000 steps can take 15-25 minutes.
# If your computer is slow, you can lower this number for a quicker (but
# less skilled) test run, for example 200_000.
TOTAL_TRAINING_STEPS = 1_000_000


# ---------------------------------------------------------
# STEP 2: Create the Lunar Lander game world (the "environment")
# ---------------------------------------------------------
# render_mode=None means "don't show the game on screen while training"
# This makes training MUCH faster.
print("Creating the Lunar Lander game world...")
env = gym.make("LunarLander-v3", render_mode=None)

# Monitor keeps track of how well the AI is doing during training
# and saves that info into the "logs" folder
env = Monitor(env, "logs/")


# ---------------------------------------------------------
# STEP 3: Create the AI "brain" using PPO
# ---------------------------------------------------------
# "MlpPolicy" just means the AI brain is a normal neural network
print("Building the AI brain (PPO model)...")
# these specific numbers below are not random - they are known to work well
# for teaching an AI to land a spaceship in this exact game
model = PPO(
    "MlpPolicy",
    env,
    verbose=1,            # this prints training progress in the terminal
    learning_rate=3e-4,   # how fast the AI learns from its mistakes
    n_steps=1024,         # how many moves it looks at before learning from them
    batch_size=64,        # how many moves it studies at once
    gae_lambda=0.98,      # helps the AI judge which moves were actually good
    gamma=0.999,          # how much the AI cares about future rewards, not just instant ones
    n_epochs=4,           # how many times it re-studies each batch of moves
    ent_coef=0.01,        # keeps the AI a little curious so it keeps trying new things
)


# ---------------------------------------------------------
# STEP 4: Train the AI
# ---------------------------------------------------------
print(f"Training the AI for {TOTAL_TRAINING_STEPS} steps. This will take a while, please be patient...")
model.learn(total_timesteps=TOTAL_TRAINING_STEPS)
print("Training finished!")


# ---------------------------------------------------------
# STEP 5: Save the trained AI brain to a file
# ---------------------------------------------------------
model.save(MODEL_SAVE_PATH)
print(f"Saved trained model to: {MODEL_SAVE_PATH}")


# ---------------------------------------------------------
# STEP 6: Test the AI to see how good it really is
# ---------------------------------------------------------
# We let the trained AI play 10 games and check its average score.
print("Testing the trained AI on 10 games...")
mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=10)
print(f"Average score: {mean_reward:.2f}  (higher is better, 200+ means a great landing)")


# ---------------------------------------------------------
# STEP 7: Save the test results as a simple JSON file
# ---------------------------------------------------------
# The website (app.py) will read this file and show it to visitors.
results = {
    "mean_reward": round(float(mean_reward), 2),
    "std_reward": round(float(std_reward), 2),
    "training_steps": TOTAL_TRAINING_STEPS,
    "eval_episodes": 10,
    "environment": "LunarLander-v3",
    "algorithm": "PPO",
    "solved": bool(mean_reward >= 200),
    "solved_threshold": 200,
}

with open(RESULTS_SAVE_PATH, "w") as f:
    json.dump(results, f, indent=4)

print(f"Saved results to: {RESULTS_SAVE_PATH}")


# ---------------------------------------------------------
# STEP 8: Make a picture (graph) showing how the AI improved over time
# ---------------------------------------------------------
print("Making the training graph picture...")

# Monitor saves a file called monitor.csv with one score per game (episode)
monitor_file = "logs/monitor.csv"

if os.path.exists(monitor_file):
    # the first line of this file is just a comment, so we skip it
    data = np.genfromtxt(monitor_file, delimiter=",", skip_header=2, names=["r", "l", "t"])
    rewards = data["r"]

    plt.figure(figsize=(10, 5))
    plt.plot(rewards, color="steelblue", label="Score per game")

    # a smoothed line is easier to read than a jumpy one
    if len(rewards) >= 10:
        smoothed = np.convolve(rewards, np.ones(10) / 10, mode="valid")
        plt.plot(smoothed, color="orange", linewidth=2, label="Smoothed average")

    plt.xlabel("Game number")
    plt.ylabel("Score")
    plt.title("How the AI's score improved during training")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(GRAPH_SAVE_PATH)
    print(f"Saved graph to: {GRAPH_SAVE_PATH}")
else:
    print("Could not find monitor.csv, so no graph was made. Training still worked fine though.")

# ---------------------------------------------------------
# STEP 9: Record a short video of the trained AI landing
# ---------------------------------------------------------
print("Recording a video of the AI playing...")
from gymnasium.wrappers import RecordVideo

video_env = gym.make("LunarLander-v3", render_mode="rgb_array")
video_env = RecordVideo(
    video_env,
    video_folder="static/videos_tmp",
    episode_trigger=lambda ep: True,   # record every episode we run below
    name_prefix="landing",
)

best_reward = -float("inf")
best_episode = 0
NUM_TRY_EPISODES = 5  # try a few games and keep the best-looking landing

for episode in range(NUM_TRY_EPISODES):
    obs, info = video_env.reset()
    done = False
    episode_reward = 0
    while not done:
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = video_env.step(action)
        episode_reward += reward
        done = terminated or truncated
    print(f"  video try {episode}: score = {episode_reward:.2f}")
    if episode_reward > best_reward:
        best_reward = episode_reward
        best_episode = episode

video_env.close()

# keep only the best-looking landing video, delete the rest
import shutil

best_video_path = f"static/videos_tmp/landing-episode-{best_episode}.mp4"
final_video_path = "static/landing_video.mp4"
if os.path.exists(best_video_path):
    shutil.copy(best_video_path, final_video_path)
    print(f"Saved best landing video (score {best_reward:.2f}) to {final_video_path}")
shutil.rmtree("static/videos_tmp", ignore_errors=True)

env.close()
print("\nAll done! You can now start app.py locally to check the website, "
      "then upload this whole folder to GitHub and deploy it on Render.")
