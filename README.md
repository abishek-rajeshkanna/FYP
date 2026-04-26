# FYP — V2X + Deep RL Traffic Simulation

A traffic-intersection simulation with V2X messaging and a reinforcement-learning
signal policy (Python / pygame backend) streamed as MJPEG to a React + Vite
frontend.

- **Backend** — Flask server that runs the pygame simulation headlessly and
  exposes an MJPEG video feed plus control endpoints (pause, replay, toggle
  broadcast circles / V2X messages).
- **Frontend** — React + TypeScript (Vite) app that embeds the live stream and
  drives the control endpoints.

## Prerequisites

- Python 3.10+ (the `py` launcher on Windows; `python3` on Ubuntu/macOS)
- Node.js 18+ and npm
- On Ubuntu, pygame needs the SDL system libraries — install once with:
  ```bash
  sudo apt update
  sudo apt install -y python3-venv python3-dev build-essential \
      libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
  ```

## Running the backend

From the project root:

### Windows (PowerShell / cmd)

```powershell
cd backend
py -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
python server.py
```

### Ubuntu / macOS (bash)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python server.py
```

Notes:

- The `venv` creation and `pip install` steps only need to be run **once** (or
  whenever dependencies change). On subsequent runs just activate the venv and
  run `python server.py`.
- `requirements.txt` installs `flask`, `flask-cors`, `pillow`, `pygame`, and
  `stable_baselines3` (which pulls in `torch`, `numpy`, and `gymnasium`). The
  `torch` download is large (a few hundred MB) — first install will take a
  while.
- **Do not** run `pip install env`. There is a Python 2-era PyPI package named
  `env` that will install successfully but break the local `backend/env/`
  imports. If you accidentally installed it, run `pip uninstall env -y`.
- The server listens on `http://localhost:5000` and exposes:
  - `GET  /video_feed` — MJPEG stream of the simulation
  - `POST /control/pause` — toggle pause
  - `POST /control/toggle-circles` — toggle broadcast circles
  - `POST /control/toggle-messages` — toggle V2X messages
  - `POST /control/replay` — rewind a few seconds
  - `GET  /control/state` — current toggle / pause flags

## Running the frontend

In a separate terminal, from the project root (commands are the same on
Windows, Ubuntu, and macOS):

```bash
cd frontend
npm install
npm run dev
```

Notes:

- `npm install` only needs to be run **once** (or when `package.json` changes).
- Vite will print a local URL (typically `http://localhost:5173`) — open it in a
  browser. The page will connect to the backend at `http://localhost:5000`, so
  make sure the backend is running first.

## Project layout

```
FYP/
├── backend/
│   ├── server.py          # Flask + MJPEG entry point
│   ├── main.py            # Standalone pygame entry point
│   ├── env/               # Simulation, lanes, vehicles, signals
│   ├── rl/                # Policy, encoder, training
│   ├── network/           # V2X channel + messages
│   └── models/            # Saved RL checkpoints
└── frontend/
    ├── src/               # React app source
    ├── index.html
    └── vite.config.ts
```
