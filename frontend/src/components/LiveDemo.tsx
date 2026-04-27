import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Pause, Play, Radio, MessageSquare, RefreshCw } from 'lucide-react'
import { useInView } from '../hooks/useInView'
import TerminalLogs from './TerminalLogs'

const API = (import.meta.env.VITE_SIM_API as string | undefined) ?? 'http://localhost:5000'

type ServerState = {
  paused: boolean
  show_circles: boolean
  show_messages: boolean
  frame_count: number
}

export default function LiveDemo() {
  const [ref, inView] = useInView()
  const [paused, setPaused] = useState(false)
  const [showCircles, setShowCircles] = useState(true)
  const [showMessages, setShowMessages] = useState(true)
  const [connected, setConnected] = useState<boolean | null>(null)
  const [streamKey, setStreamKey] = useState(0)

  useEffect(() => {
    let cancelled = false
    fetch(`${API}/control/state`)
      .then((r) => r.json())
      .then((s: ServerState) => {
        if (cancelled) return
        setPaused(s.paused)
        setShowCircles(s.show_circles)
        setShowMessages(s.show_messages)
        setConnected(true)
      })
      .catch(() => !cancelled && setConnected(false))
    return () => {
      cancelled = true
    }
  }, [streamKey])

  async function post<T>(path: string): Promise<T | null> {
    try {
      const r = await fetch(`${API}${path}`, { method: 'POST' })
      if (!r.ok) throw new Error(String(r.status))
      return (await r.json()) as T
    } catch {
      setConnected(false)
      return null
    }
  }

  const togglePause = async () => {
    const r = await post<{ paused: boolean }>('/control/pause')
    if (r) setPaused(r.paused)
  }
  const toggleCircles = async () => {
    const r = await post<{ show_circles: boolean }>('/control/toggle-circles')
    if (r) setShowCircles(r.show_circles)
  }
  const toggleMessages = async () => {
    const r = await post<{ show_messages: boolean }>('/control/toggle-messages')
    if (r) setShowMessages(r.show_messages)
  }
  const reconnect = () => {
    setConnected(null)
    setStreamKey((k) => k + 1)
  }

  return (
    <section className="section" id="demo" ref={ref}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5 }}
      >
        <div className="section-label">Live Demo</div>
        <h2 className="section-title">Interactive Simulation</h2>
        <p className="section-desc">
          The pygame simulation is rendered headlessly on a Flask server and streamed to the browser as MJPEG.
          Use the controls below — they map to the keyboard shortcuts from the standalone runner.
        </p>
      </motion.div>

      <motion.div
        className="demo-frame"
        initial={{ opacity: 0, y: 30 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <div className="demo-stage">
          {connected === false ? (
            <div className="demo-error">
              <div className="demo-error-title">Backend not reachable</div>
              <div className="demo-error-msg">
                Start the simulation server: <code>cd backend &amp;&amp; python server.py</code>
              </div>
              <button className="demo-btn" onClick={reconnect}>
                <RefreshCw size={14} /> Retry
              </button>
            </div>
          ) : (
            <img
              key={streamKey}
              className="demo-stream"
              src={`${API}/video_feed?k=${streamKey}`}
              alt="Live simulation stream"
              onError={() => setConnected(false)}
              onLoad={() => setConnected(true)}
            />
          )}
        </div>

        <div className="demo-controls">
          <button className="demo-btn" onClick={togglePause} disabled={connected === false}>
            {paused ? <Play size={14} /> : <Pause size={14} />}
            <span>{paused ? 'Resume' : 'Pause'}</span>
            <span className="demo-kbd">SPACE</span>
          </button>
          <button className="demo-btn" onClick={toggleCircles} disabled={connected === false}>
            <Radio size={14} />
            <span>{showCircles ? 'Hide' : 'Show'} Broadcast Circles</span>
            <span className="demo-kbd">B</span>
          </button>
          <button className="demo-btn" onClick={toggleMessages} disabled={connected === false}>
            <MessageSquare size={14} />
            <span>{showMessages ? 'Hide' : 'Show'} V2X Messages</span>
            <span className="demo-kbd">M</span>
          </button>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <TerminalLogs />
      </motion.div>
    </section>
  )
}
