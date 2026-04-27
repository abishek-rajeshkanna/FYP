import { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'

const API = (import.meta.env.VITE_SIM_API as string | undefined) ?? 'http://localhost:5000'

type DRLEntry = {
  _ts: number
  agent: string
  lane: string
  speed: number
  action_id: number
  action: string
  state_values: number[]
}

type MAPPOEntry = {
  _ts: number
  state: number[]
  action: number
  timer: number
}

type QoSSample = {
  range: number
  packet_rate: number
  density: number
  contention: number
}

type QoSEntry = {
  _ts: number
  vehicle: string
  location: string
  samples: number
  data: QoSSample[]
}

type LogData = {
  drl: DRLEntry[]
  mappo: MAPPOEntry[]
  qos: QoSEntry[]
}

type Tab = 'drl' | 'mappo' | 'qos'

const TABS: { id: Tab; label: string; color: string }[] = [
  { id: 'drl',   label: 'DRL Lane Change',              color: 'blue'   },
  { id: 'mappo', label: 'MAPPO Traffic Signal Control', color: 'green'  },
  { id: 'qos',   label: 'QoS Network Parameter Update', color: 'purple' },
]

const MAPPO_STATE_DESC = [
  'North Queue', 'South Queue', 'East Queue', 'West Queue',
  'Signal Phase', 'Neighbor Queue (1)', 'Neighbor Queue (2)', 'EV Distance',
]

const SIGNAL_PHASE_MAP: Record<string, string> = {
  HORIZONTAL_GREEN:  'EW Through Green',
  VERTICAL_GREEN:    'NS Through Green',
  HORIZONTAL_YELLOW: 'EW Yellow',
  VERTICAL_YELLOW:   'NS Yellow',
  EW_THROUGH:        'EW Through Green',
  NS_THROUGH:        'NS Through Green',
  EW_LEFT:           'EW Left-Turn Green',
  NS_LEFT:           'NS Left-Turn Green',
}

const MAPPO_ACTION_MAP: Record<number, string> = {
  0: 'EW Through Green',
  1: 'NS Through Green',
  2: 'EW Left-Turn Green',
  3: 'NS Left-Turn Green',
}

function fmt(n: number) {
  return n.toFixed ? n.toFixed(2) : String(n)
}

function DRLBlock({ entry }: { entry: DRLEntry }) {
  const vals = entry.state_values ?? []
  return (
    <div className="tlog-entry">
      <div className="tlog-ts">{new Date(entry._ts * 1000).toLocaleTimeString()}</div>
      <div className="tlog-line dim">{'================================================'}</div>
      <div className="tlog-line accent2">{'        EMERGENCY VEHICLE AGENT DECISION'}</div>
      <div className="tlog-line dim">{'------------------------------------------------'}</div>
      <div className="tlog-line">
        <span className="tlog-key">Agent                </span>
        <span className="tlog-sep">| </span>
        <span className="tlog-val orange">{entry.agent}</span>
      </div>
      <div className="tlog-line">
        <span className="tlog-key">Current Lane         </span>
        <span className="tlog-sep">| </span>
        <span className="tlog-val accent2">{entry.lane}</span>
      </div>
      <div className="tlog-line">
        <span className="tlog-key">Speed                </span>
        <span className="tlog-sep">| </span>
        <span className="tlog-val">{fmt(entry.speed)} m/s</span>
      </div>
      <div className="tlog-line">
        <span className="tlog-key">Action ID            </span>
        <span className="tlog-sep">| </span>
        <span className="tlog-val purple">{entry.action_id}</span>
      </div>
      <div className="tlog-line">
        <span className="tlog-key">Action Meaning       </span>
        <span className="tlog-sep">| </span>
        <span className="tlog-val green">{entry.action}</span>
      </div>
      <div className="tlog-line dim">{'================================================'}</div>
      <div className="tlog-spacer" />
      <div className="tlog-line accent2 bold">STATE VECTOR DESCRIPTION</div>
      <div className="tlog-line muted">{'Neighbors (x6): [Lane, Speed, Acceleration, RelDistance]'}</div>
      <div className="tlog-line muted">{'Ego Vehicle   : [Lane, Speed, Acceleration, RelDistance, Position]'}</div>
      <div className="tlog-line muted">{'Total Features: 29'}</div>
      <div className="tlog-spacer" />
      <div className="tlog-line accent2 bold">STATE VECTOR VALUES</div>
      <div className="tlog-state-grid">
        {vals.map((v, i) => (
          <span key={i} className="tlog-state-chip">{fmt(v)}</span>
        ))}
      </div>
    </div>
  )
}

function MAPPOBlock({ entry }: { entry: MAPPOEntry }) {
  return (
    <div className="tlog-entry">
      <div className="tlog-ts">{new Date(entry._ts * 1000).toLocaleTimeString()}</div>
      <div className="tlog-line green bold">STATE VECTOR DESCRIPTION FOR MAPPO</div>
      <div className="tlog-line muted">
        {'[North Queue, South Queue, East Queue, West Queue,'}
      </div>
      <div className="tlog-line muted">
        {' Signal Phase, Neighbor Queue (1), Neighbor Queue (2), EV Distance]'}
      </div>
      <div className="tlog-spacer" />
      <div className="tlog-mappo-state">
        {MAPPO_STATE_DESC.map((label, i) => {
          const raw = entry.state?.[i]
          const display = i === 4
            ? (SIGNAL_PHASE_MAP[String(raw)] ?? String(raw ?? '—'))
            : (raw ?? '—')
          return (
            <div key={i} className="tlog-mappo-row">
              <span className="tlog-mappo-label">{label}</span>
              <span className="tlog-mappo-value">{display}</span>
            </div>
          )
        })}
      </div>
      <div className="tlog-spacer" />
      <div className="tlog-line dim">{'============================'}</div>
      <div className="tlog-line">
        <span className="tlog-key">RL ACTION</span>
        <span className="tlog-sep"> | </span>
        <span className="tlog-val green">{entry.action} — {MAPPO_ACTION_MAP[entry.action] ?? 'UNKNOWN'}</span>
      </div>
      <div className="tlog-line">
        <span className="tlog-key">Timer    </span>
        <span className="tlog-sep"> | </span>
        <span className="tlog-val accent2">{entry.timer}</span>
      </div>
      <div className="tlog-line dim">{'============================'}</div>
    </div>
  )
}

function QoSBlock({ entry }: { entry: QoSEntry }) {
  const samples = entry.data ?? []
  const header = samples.map((_, i) => `T${i + 1}`).join(' | ')
  const ranges      = samples.map(s => String(s.range)).join(' | ')
  const packets     = samples.map(s => String(s.packet_rate)).join(' | ')
  const densities   = samples.map(s => String(s.density)).join(' | ')
  const contentions = samples.map(s => String(s.contention)).join(' | ')

  return (
    <div className="tlog-entry">
      <div className="tlog-ts">{new Date(entry._ts * 1000).toLocaleTimeString()}</div>
      <div className="tlog-line dim">{'------------------------------------------------------------'}</div>
      <div className="tlog-line">
        <span className="tlog-key">Vehicle  </span>
        <span className="tlog-sep">: </span>
        <span className="tlog-val orange">{entry.vehicle}</span>
      </div>
      <div className="tlog-line">
        <span className="tlog-key">Location </span>
        <span className="tlog-sep">: </span>
        <span className="tlog-val accent2">{entry.location}</span>
      </div>
      <div className="tlog-line">
        <span className="tlog-key">Samples  </span>
        <span className="tlog-sep">: </span>
        <span className="tlog-val purple">{entry.samples}</span>
      </div>
      <div className="tlog-line dim">{'------------------------------------------------------------'}</div>
      <div className="tlog-qos-table">
        <div className="tlog-qos-row header">
          <span className="tlog-qos-param">Parameters</span>
          {samples.map((_, i) => (
            <span key={i} className="tlog-qos-cell header-cell">T{i + 1}</span>
          ))}
        </div>
        <div className="tlog-qos-divider" />
        {[
          { label: 'Range (m)',       values: samples.map(s => s.range),       color: 'green'  },
          { label: 'Packet Rate',     values: samples.map(s => s.packet_rate), color: 'blue'   },
          { label: 'Density',         values: samples.map(s => s.density),     color: 'purple' },
          { label: 'Contention (ms)', values: samples.map(s => s.contention),  color: 'orange' },
        ].map(row => (
          <div key={row.label} className="tlog-qos-row">
            <span className="tlog-qos-param">{row.label}</span>
            {row.values.map((v, i) => (
              <span key={i} className={`tlog-qos-cell ${row.color}`}>{v}</span>
            ))}
          </div>
        ))}
      </div>
      <div className="tlog-line dim">{'------------------------------------------------------------'}</div>
      {/* hidden plain text for reference */}
      <div style={{ display: 'none' }}>
        {`Parameters | ${header}\nRange (m) | ${ranges}\nPacket Rate | ${packets}\nDensity | ${densities}\nContention (ms) | ${contentions}`}
      </div>
    </div>
  )
}

function EmptyState({ module }: { module: Tab }) {
  const hints: Record<Tab, string> = {
    drl:   'Logs appear when an emergency vehicle makes a lane-change decision.',
    mappo: 'Logs appear every ~7.5 seconds when the MAPPO policy runs.',
    qos:   'Logs appear when an emergency vehicle completes a lane traversal.',
  }
  return (
    <div className="tlog-empty">
      <div className="tlog-empty-icon">▋</div>
      <div className="tlog-empty-msg">Waiting for logs…</div>
      <div className="tlog-empty-hint">{hints[module]}</div>
    </div>
  )
}

export default function TerminalLogs() {
  const [active, setActive] = useState<Tab>('drl')
  const [logs, setLogs] = useState<LogData>({ drl: [], mappo: [], qos: [] })
  const [connected, setConnected] = useState(true)
  const bodyRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    let cancelled = false
    const poll = async () => {
      try {
        const r = await fetch(`${API}/logs`)
        if (!r.ok) throw new Error(String(r.status))
        const data: LogData = await r.json()
        if (!cancelled) {
          setLogs(data)
          setConnected(true)
        }
      } catch {
        if (!cancelled) setConnected(false)
      }
    }
    poll()
    const id = setInterval(poll, 2000)
    return () => { cancelled = true; clearInterval(id) }
  }, [])

  // Auto-scroll to bottom when new logs arrive for active tab
  useEffect(() => {
    if (bodyRef.current) {
      bodyRef.current.scrollTop = bodyRef.current.scrollHeight
    }
  }, [logs, active])

  const entries = logs[active] ?? []

  return (
    <div className="tlog-wrapper">
      <div className="tlog-header">
        <div className="tlog-title-row">
          <span className="tlog-title">Module Terminal Logs</span>
          <span className={`tlog-status ${connected ? 'connected' : 'disconnected'}`}>
            <span className="tlog-status-dot" />
            {connected ? 'Live' : 'Offline'}
          </span>
        </div>
        <div className="tlog-tabs">
          {TABS.map(tab => (
            <button
              key={tab.id}
              className={`tlog-tab ${tab.color} ${active === tab.id ? 'active' : ''}`}
              onClick={() => setActive(tab.id)}
            >
              {tab.label}
              {logs[tab.id].length > 0 && (
                <span className="tlog-badge">{logs[tab.id].length}</span>
              )}
            </button>
          ))}
        </div>
      </div>

      <div className="tlog-body" ref={bodyRef}>
        {entries.length === 0 ? (
          <EmptyState module={active} />
        ) : (
          <motion.div
            key={active}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.2 }}
          >
            {entries.map((entry, i) => (
              <div key={i}>
                {active === 'drl'   && <DRLBlock   entry={entry as DRLEntry}   />}
                {active === 'mappo' && <MAPPOBlock entry={entry as MAPPOEntry} />}
                {active === 'qos'   && <QoSBlock   entry={entry as QoSEntry}   />}
              </div>
            ))}
          </motion.div>
        )}
      </div>
    </div>
  )
}
