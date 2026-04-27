"""
Headless Flask server that runs the pygame + RL simulation in a background
thread and streams the rendered surface as MJPEG so a web frontend can embed
it in an <img> tag.

Run:
    pip install flask flask-cors pillow
    python server.py

Endpoints:
    GET  /video_feed              -> multipart/x-mixed-replace MJPEG stream
    POST /control/pause           -> toggle pause (SPACE)
    POST /control/toggle-circles  -> toggle broadcast circles (B)
    POST /control/toggle-messages -> toggle V2X messages (M)
    POST /control/replay          -> rewind a few seconds (LEFT arrow)
    GET  /control/state           -> current toggle/pause flags
"""

import os
# Run pygame without opening an OS window — must be set before importing pygame.
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import io
import threading
import time

import pygame
from PIL import Image
from flask import Flask, Response, jsonify
from flask_cors import CORS

from env.simulation import Simulation
from rl.signal_policy import SignalPolicy
from rl.state_encoder import StateEncoder
import log_store


WIDTH = 1250
HEIGHT = 670
FPS = 40
JPEG_QUALITY = 75
DECISION_INTERVAL = 300
HISTORY_LIMIT = 200
REPLAY_STEPS = 30


pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

sim = Simulation(WIDTH, HEIGHT)
policy = SignalPolicy()
encoder = StateEncoder()

state_lock = threading.Lock()
frame_lock = threading.Lock()
latest_frame_jpeg: bytes | None = None

paused = False
frame_count = 0
history: list = []


def _horizontal_queue(stats):
    return (
        stats["W0"]["queue"]
        + stats["W1"]["queue"]
        + stats["E0"]["queue"]
        + stats["E1"]["queue"]
    )


def _vertical_queue(stats):
    return (
        stats["N0"]["queue"]
        + stats["N1"]["queue"]
        + stats["S0"]["queue"]
        + stats["S1"]["queue"]
    )


def _sim_loop():
    global frame_count, latest_frame_jpeg

    pause_font = pygame.font.SysFont(None, 48)

    while True:
        clock.tick(FPS)
        frame_count += 1
        # Drain SDL's event queue so it doesn't fill up under the dummy driver.
        pygame.event.pump()

        with state_lock:
            if frame_count % DECISION_INTERVAL == 0:
                lane_stats = sim.get_lane_statistics()
                ev_data = sim.detect_ev_lanes()
                state = encoder.encode(lane_stats, ev_data, sim.signal)
                action = policy.act(state)

                hq = _horizontal_queue(lane_stats)
                vq = _vertical_queue(lane_stats)
                horizontal_green = sim.signal.is_horizontal_green()
                vertical_green = sim.signal.is_vertical_green()

                # MAPPO state vector logging
                north_q = lane_stats["N0"]["queue"] + lane_stats["N1"]["queue"]
                south_q = lane_stats["S0"]["queue"] + lane_stats["S1"]["queue"]
                east_q  = lane_stats["E0"]["queue"] + lane_stats["E1"]["queue"]
                west_q  = lane_stats["W0"]["queue"] + lane_stats["W1"]["queue"]
                neighbor_q1 = east_q + west_q
                neighbor_q2 = north_q + south_q
                ev_dist = -1
                for vehicle, controller in sim.vehicles:
                    if vehicle.is_emergency:
                        ev_dist = round(
                            (1 - controller.t) * controller.lane.length * sim.PIXEL_TO_METER, 2
                        )
                        break
                m_state = [north_q, south_q, east_q, west_q,
                           sim.signal.phase, neighbor_q1, neighbor_q2, ev_dist]
                if not paused:
                    log_store.add("mappo", {
                        "state": m_state,
                        "action": int(action),
                        "timer": sim.signal.timer,
                    })

                if horizontal_green and vq > hq + 1:
                    sim.signal.switch_phase()
                elif vertical_green and hq > vq + 1:
                    sim.signal.switch_phase()
                elif action == 1:
                    sim.signal.switch_phase()
                elif action == 2:
                    sim.signal.extend_green()

            sim.paused = paused
            if not paused:
                sim.update()
                history.append(sim.get_state())
                if len(history) > HISTORY_LIMIT:
                    history.pop(0)

            screen.fill((30, 30, 30))
            sim.draw(screen)

            if paused:
                text = pause_font.render("PAUSED", True, (255, 255, 255))
                screen.blit(text, (WIDTH // 2 - 100, HEIGHT // 2 - 24))

            raw = pygame.image.tostring(screen, "RGB")

        img = Image.frombytes("RGB", (WIDTH, HEIGHT), raw)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=JPEG_QUALITY)
        with frame_lock:
            latest_frame_jpeg = buf.getvalue()


app = Flask(__name__)
CORS(app)


def _mjpeg_generator():
    boundary = b"--frame\r\n"
    interval = 1.0 / FPS
    last_sent: bytes | None = None
    while True:
        with frame_lock:
            frame = latest_frame_jpeg
        if frame is None or frame is last_sent:
            time.sleep(interval / 2)
            continue
        last_sent = frame
        yield (
            boundary
            + b"Content-Type: image/jpeg\r\n"
            + b"Content-Length: " + str(len(frame)).encode() + b"\r\n\r\n"
            + frame
            + b"\r\n"
        )
        time.sleep(interval)


@app.route("/video_feed")
def video_feed():
    return Response(
        _mjpeg_generator(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@app.route("/control/pause", methods=["POST"])
def control_pause():
    global paused
    paused = not paused
    return jsonify({"paused": paused})


@app.route("/control/toggle-circles", methods=["POST"])
def control_toggle_circles():
    with state_lock:
        sim.show_circles = not sim.show_circles
        value = sim.show_circles
    return jsonify({"show_circles": value})


@app.route("/control/toggle-messages", methods=["POST"])
def control_toggle_messages():
    with state_lock:
        sim.show_messages = not sim.show_messages
        value = sim.show_messages
    return jsonify({"show_messages": value})


@app.route("/control/replay", methods=["POST"])
def control_replay():
    with state_lock:
        steps = min(REPLAY_STEPS, len(history))
        for _ in range(steps):
            if history:
                history.pop()
        if history:
            sim.set_state(history[-1])
    return jsonify({"replayed_steps": steps})


@app.route("/control/state", methods=["GET"])
def control_state():
    with state_lock:
        return jsonify(
            {
                "paused": paused,
                "show_circles": sim.show_circles,
                "show_messages": sim.show_messages,
                "frame_count": frame_count,
            }
        )


@app.route("/logs", methods=["GET"])
def get_logs():
    return jsonify(log_store.get_all())


def main():
    threading.Thread(target=_sim_loop, daemon=True).start()
    # threaded=True so MJPEG generators don't block control endpoints.
    app.run(host="0.0.0.0", port=5000, threaded=True, debug=False)


if __name__ == "__main__":
    main()
