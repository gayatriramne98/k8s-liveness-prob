"""
Liveness Probe Demo App
------------------------
A tiny Flask app used to demonstrate Kubernetes liveness probes.

Behaviour:
  GET /            -> simple "alive" message with uptime
  GET /healthz     -> returns 200 while healthy, 500 once "unhealthy"
  GET /toggle      -> manually flips the healthy flag (for live demos)

Auto-degrade mode (default ON):
  After AUTO_FAIL_AFTER seconds of uptime, /healthz starts returning 500
  automatically, simulating an app that has "hung" (e.g. deadlock, stuck
  thread, memory leak). This lets students SEE Kubernetes restart the
  container on its own, without needing to manually break it.

Env vars:
  AUTO_FAIL_AFTER   seconds before the app auto-degrades (default: 45, 0 disables)
"""

import os
import time
from flask import Flask, jsonify

app = Flask(__name__)

START_TIME = time.time()
AUTO_FAIL_AFTER = int(os.environ.get("AUTO_FAIL_AFTER", "45"))

# Manual override flag (toggled via /toggle)
manual_unhealthy = False


def uptime_seconds():
    return int(time.time() - START_TIME)


def is_healthy():
    if manual_unhealthy:
        return False
    if AUTO_FAIL_AFTER > 0 and uptime_seconds() >= AUTO_FAIL_AFTER:
        return False
    return True


@app.route("/")
def index():
    return jsonify(
        message="liveness-probe-demo app is running",
        uptime_seconds=uptime_seconds(),
        healthy=is_healthy(),
    )


@app.route("/healthz")
def healthz():
    if is_healthy():
        return jsonify(status="ok", uptime_seconds=uptime_seconds()), 200
    return jsonify(status="unhealthy", uptime_seconds=uptime_seconds()), 500


@app.route("/toggle")
def toggle():
    global manual_unhealthy
    manual_unhealthy = not manual_unhealthy
    return jsonify(manual_unhealthy=manual_unhealthy)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
