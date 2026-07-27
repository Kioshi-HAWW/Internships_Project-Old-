"""
app.py
------
This is a small website. It does NOT train any AI by itself.
It just reads the results that train.py already saved, and shows them
nicely on a webpage. This is what we put on Render.

Because this file is simple and light, Render can start it quickly
and it will always answer with status 200 (which means "everything is OK").
"""

import json
import os
from flask import Flask, render_template

app = Flask(__name__)

RESULTS_FILE = os.path.join("static", "results.json")
GRAPH_FILE = os.path.join("static", "training_reward_graph.png")
VIDEO_FILE = os.path.join("static", "landing_video.mp4")


def load_results():
    """
    This little function tries to read our saved results.
    If the file is not there yet (for example, you haven't run
    train.py yet), we just show some placeholder text instead of crashing.
    """
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, "r") as f:
            return json.load(f)
    else:
        # placeholder info shown until train.py has been run
        return {
            "mean_reward": "Not trained yet",
            "std_reward": "-",
            "training_steps": "-",
            "eval_episodes": "-",
            "environment": "LunarLander-v3",
            "algorithm": "PPO",
        }


@app.route("/")
def home():
    """
    This is the main page. When someone opens the website link,
    this function runs and sends back a webpage. Flask automatically
    replies with status 200 here unless something goes wrong.
    """
    results = load_results()
    graph_exists = os.path.exists(GRAPH_FILE)
    video_exists = os.path.exists(VIDEO_FILE)
    return render_template(
        "index.html", results=results, graph_exists=graph_exists, video_exists=video_exists
    )


@app.route("/health")
def health():
    """
    A tiny extra page just to check the website is alive.
    Render (or your teacher) can visit /health and should always see "OK".
    """
    return "OK", 200


if __name__ == "__main__":
    # This part only runs when you test the website on your own computer.
    # On Render, gunicorn will start the app instead (see the Procfile).
    app.run(host="0.0.0.0", port=5000, debug=True)
