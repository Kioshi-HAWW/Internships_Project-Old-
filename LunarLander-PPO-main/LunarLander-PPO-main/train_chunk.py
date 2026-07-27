import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.evaluation import evaluate_policy
import os, json, time, sys

CHUNK_STEPS = int(sys.argv[1]) if len(sys.argv) > 1 else 150_000
MODEL_PATH = "models/ppo_working.zip"
STATE_PATH = "models/train_state.json"

os.makedirs("models", exist_ok=True)

env = Monitor(gym.make("LunarLander-v3"), "logs/")

if os.path.exists(MODEL_PATH):
    model = PPO.load(MODEL_PATH, env=env)
    print("Loaded existing model, continuing training...")
else:
    model = PPO(
        "MlpPolicy",
        env,
        n_steps=1024,
        batch_size=64,
        gae_lambda=0.98,
        gamma=0.999,
        n_epochs=4,
        ent_coef=0.01,
        learning_rate=3e-4,
        verbose=0,
    )
    print("Created new model...")

if os.path.exists(STATE_PATH):
    with open(STATE_PATH) as f:
        state = json.load(f)
else:
    state = {"total_steps": 0}

t0 = time.time()
model.learn(total_timesteps=CHUNK_STEPS, reset_num_timesteps=False)
elapsed = time.time() - t0

state["total_steps"] += CHUNK_STEPS
model.save(MODEL_PATH)

eval_env = Monitor(gym.make("LunarLander-v3"), "logs/eval_tmp/")
mean_r, std_r = evaluate_policy(model, eval_env, n_eval_episodes=10, deterministic=True)
state["last_mean_reward"] = float(mean_r)
state["last_std_reward"] = float(std_r)

with open(STATE_PATH, "w") as f:
    json.dump(state, f, indent=2)

print(f"Chunk done in {elapsed:.1f}s | total_steps so far: {state['total_steps']} | "
      f"eval mean reward: {mean_r:.2f} +/- {std_r:.2f}")
