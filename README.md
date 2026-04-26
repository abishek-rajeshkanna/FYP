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

- Python 3.10+ (with `py` launcher on Windows)
- Node.js 18+ and npm
- Windows shell commands are shown below; on macOS/Linux replace
  `venv\Scripts\activate` with `source venv/bin/activate`.

## Running the backend

From the project root:

```bash
cd backend
py -m venv venv
venv\Scripts\activate
python -m pip install flask flask-cors pillow
python server.py
```

Notes:

- The `py -m venv venv` and `pip install ...` steps only need to be run **once**
  (or whenever dependencies change). On subsequent runs just activate the venv
  and run `python server.py`.
- The server listens on `http://localhost:5000` and exposes:
  - `GET  /video_feed` — MJPEG stream of the simulation
  - `POST /control/pause` — toggle pause
  - `POST /control/toggle-circles` — toggle broadcast circles
  - `POST /control/toggle-messages` — toggle V2X messages
  - `POST /control/replay` — rewind a few seconds
  - `GET  /control/state` — current toggle / pause flags

## Running the frontend

In a separate terminal, from the project root:

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
