# Lunar Lander PPO Project (Reinforcement Learning)

This project trains an AI to land a spaceship safely, using:
- **Gymnasium** — the game world (LunarLander-v3)
- **Stable-Baselines3 (PPO)** — the learning algorithm
- **Flask** — a small website that shows the AI's results

The project has two parts:
1. **Training** (`train.py`) — you run this on your own computer, one time, to teach the AI.
2. **Website** (`app.py`) — this is the small, light website you put on Render so your teacher can see the results online.

We split it this way because the training part needs big, heavy packages (PyTorch, Box2D) that are slow and sometimes tricky to install on free hosting. The website part only needs Flask, so it deploys fast and reliably.

**A fully trained model is already included in this folder** — it was trained for 1,050,000 steps and reaches an average score of **236.64** over 30 test games (a score above 200 is considered "solved," meaning the AI reliably lands the spaceship safely). A real landing video and a real training progress graph are already included too, so the website works and looks complete the moment you deploy it. You do not have to retrain anything to submit this.

If you'd like to retrain it yourself anyway (for example, to understand the code better), instructions are below.

---

## Folder overview

```
LunarLander-PPO/
├── train.py                     # Trains the AI (run this on your computer)
├── app.py                       # The website Flask shows on Render
├── requirements.txt             # Small package list, used by Render
├── requirements-training.txt    # Big package list, used only for training
├── Procfile                     # Tells Render how to start the website
├── runtime.txt                  # Tells Render which Python version to use
├── models/
│   └── ppo_lunar_lander.zip     # The saved, trained AI brain (already solved, 236.64 avg score)
├── static/
│   ├── results.json             # The AI's test scores
│   ├── training_reward_graph.png # Picture showing training progress
│   └── landing_video.mp4        # A real video of the AI landing
├── templates/
│   └── index.html               # The webpage design
└── logs/
    └── monitor.csv              # Raw training log (created by train.py)
```

---

## Step 1 (optional): Retrain the AI yourself

You don't need to do this to submit — the included model is already trained and solved (score 236.64). Only do this if you want to see the training happen yourself or understand the code better.

1. Open a terminal inside this folder
2. Install the training packages:
   ```
   pip install -r requirements-training.txt
   ```
3. Run the training:
   ```
   python train.py
   ```
4. Wait. With the default setting (1,000,000 steps) this can take 15–25 minutes on a normal laptop. You will see numbers printing in the terminal — that's normal, it's the AI learning. A score of 200+ means it's solved.
5. When it's done, these files will be updated automatically:
   - `models/ppo_lunar_lander.zip` (the trained AI)
   - `static/results.json` (test scores)
   - `static/training_reward_graph.png` (progress picture)
   - `static/landing_video.mp4` (a video of the AI landing)

**Tip:** If your computer is slow and 1,000,000 steps takes too long, you can lower this line in `train.py` for a quicker test run (the score will be worse though):
```python
TOTAL_TRAINING_STEPS = 1_000_000
```

---

## Step 2: Test the website on your own computer (optional)

1. Install the website packages:
   ```
   pip install -r requirements.txt
   ```
2. Run:
   ```
   python app.py
   ```
3. Open your browser and go to: `http://localhost:5000`
4. You should see your AI's results on the page.

---

## Step 3: Upload to GitHub

1. Create a new repository on GitHub (for example: `lunar-lander-ppo`)
2. Upload this whole folder to that repository (all files, including the `models` and `static` folders)

---

## Step 4: Deploy on Render

1. Go to [render.com](https://render.com) and log in
2. Click **New +** → **Web Service**
3. Connect your GitHub repository
4. Fill in these settings:
   - **Root Directory:** leave empty (unless you put this folder inside another folder — then type the folder name)
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Python Version:** this is already set by the `runtime.txt` file (3.11.9)
5. Click **Create Web Service**
6. Wait a few minutes for the build to finish
7. Once it's live, open the Render link — you should see your Lunar Lander results page, and it will return a status of 200 (meaning it's working properly)

---

## Step 5: Submit

Copy the Render website link (it looks like `https://your-app-name.onrender.com`) and submit that , open it and see:
- Which algorithm you used (PPO)
- How many steps you trained for
- The AI's average score (236.64, which is above the 200 "solved" mark)
- A video of the AI actually landing the spaceship
- A graph of how the AI improved over time

---

## Common problems and fixes

**"Application failed to respond" on Render**
Double check the Start Command is exactly `gunicorn app:app` and that `gunicorn` is listed in `requirements.txt`.

**Build fails on Render**
Make sure the Root Directory setting matches where your files actually are in the GitHub repo. If you uploaded the folder itself (not just its contents), you may need to set Root Directory to `LunarLander-PPO`.

**Training is very slow on my computer**
Lower `TOTAL_TRAINING_STEPS` in `train.py` to something smaller like `50000` for a quicker test run, then raise it later for a better AI. There's also a bonus file included, `train_chunk.py`, which trains in smaller pieces you can stop and resume — useful if your computer can't stay on for 20+ minutes at once. Run it like this, as many times as you want:
```
python train_chunk.py 200000
```
Each time you run it, it picks up where it left off and trains 200,000 more steps. Keep running it until the printed "eval mean reward" reaches 200 or higher, then copy `models/ppo_working.zip` over `models/ppo_lunar_lander.zip`.

**I get an error about Box2D when training**
Box2D sometimes needs an extra tool called `swig` installed on your computer first. On Windows, running `pip install gymnasium[box2d]` again after installing `swig` usually fixes it. This is only needed for training on your computer, not for the Render website.
