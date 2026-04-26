import { motion } from 'framer-motion'
import { useInView } from '../hooks/useInView'
import SignalArchDiagram from './SignalArchDiagram'

const stateFields = [
  { label: 'Queue counts (4 lanes)', fields: ['q_north', 'q_south', 'q_east', 'q_west'], color: 'blue' },
  { label: 'Current phase', fields: ['phase'], color: 'purple' },
  { label: 'Neighbor phases (×2)', fields: ['neighbor_phase_0', 'neighbor_phase_1'], color: 'green' },
  { label: 'EV proximity', fields: ['ev_distance'], color: 'orange' as 'blue' | 'green' | 'purple' },
]

export default function MARLSection() {
  const [ref, inView] = useInView()

  return (
    <section className="section" id="marl" ref={ref}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5 }}
      >
        <div className="section-label">Model 2</div>
        <h2 className="section-title">MARL — Multi-Agent Signal Control</h2>
        <p className="section-desc">
          Four traffic signal agents control a cross-junction (+) network under the
          Centralized Training, Decentralized Execution (CTDE) paradigm. Each agent
          observes only its local 8-dimensional state while a shared centralized critic
          evaluates the global joint state during training.
        </p>
      </motion.div>

      <motion.div
        className="marl-grid"
        initial={{ opacity: 0, y: 30 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5, delay: 0.15 }}
      >
        {/* Junction topology */}
        <div className="marl-topology">
          <div className="topology-title">Cross-Junction (+) Topology — 4 Signal Agents</div>
          <div className="plus-junction">
            <div className="plus-row plus-top"><div className="plus-road v" /></div>
            <div className="plus-row plus-mid">
              <div className="plus-road h" />
              <div className="plus-center">
                <div className="plus-signal n"><span>N</span></div>
                <div className="plus-signal-row">
                  <div className="plus-signal w"><span>W</span></div>
                  <div className="plus-core" />
                  <div className="plus-signal e"><span>E</span></div>
                </div>
                <div className="plus-signal s"><span>S</span></div>
              </div>
              <div className="plus-road h" />
            </div>
            <div className="plus-row plus-bot"><div className="plus-road v" /></div>
          </div>
          <div style={{ marginTop: '1.5rem' }}>
            <div className="state-group-label" style={{ marginBottom: '0.75rem' }}>Per-Agent State — 8 dimensions</div>
            <div className="state-vector">
              {stateFields.map(g => (
                <div className="state-group" key={g.label} style={{ marginBottom: '0.5rem' }}>
                  <div className="state-group-label">{g.label}</div>
                  <div className="state-fields">
                    {g.fields.map(f => (
                      <span key={f} className={`state-field ${g.color}`}>{f}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Reward */}
        <div className="reward-breakdown">
          <div className="topology-title">Reward Function</div>
          <div className="reward-formula">
            R = <span className="neg">- queue</span>{' '}
            <span className="neg">- 0.5 × wait</span>{' '}
            <span className="pos">+ 3 × ev_speed</span>{' '}
            <span className="neg">- 5 × ev_delay</span>
          </div>
          <div className="reward-items">
            {[
              { sign: '-', color: 'neg', text: 'Total halting vehicles across all lanes' },
              { sign: '-', color: 'neg', text: '0.5 × cumulative lane waiting time' },
              { sign: '+', color: 'pos', text: '3 × current EV speed (reward fast passage)' },
              { sign: '-', color: 'neg', text: '5 × EV speed deficit below desired speed' },
            ].map((r, i) => (
              <div className="reward-item" key={i}>
                <span className={`reward-item-sign ${r.color}`}>{r.sign}</span>
                <span className="reward-item-text">{r.text}</span>
              </div>
            ))}
          </div>
        </div>
      </motion.div>

      {/* CTDE explanation */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5, delay: 0.3 }}
        style={{ marginTop: '3rem' }}
      >
        <div className="arch-split">
          <div className="arch-panel">
            <div className="arch-panel-header">
              <div className="arch-panel-dot blue" />
              <div className="arch-panel-title">DECENTRALIZED ACTORS (×4)</div>
            </div>
            <div className="arch-panel-body">
              <div className="network-diagram">
                {[
                  { label: 'Local State', bar: 'input', text: '8-dim local observation', size: '8' },
                  { label: '', arrow: true },
                  { label: 'Hidden 1', bar: 'h1', text: 'Linear(8→64) → ReLU', size: '64' },
                  { label: '', arrow: true },
                  { label: 'Hidden 2', bar: 'h2', text: 'Linear(64→64) → ReLU', size: '64' },
                  { label: '', arrow: true },
                  { label: 'Output', bar: 'output', text: 'Logits → phase {0,1}', size: '2' },
                ].map((row, i) =>
                  (row as any).arrow ? (
                    <div key={i} className="net-arrow">↓</div>
                  ) : (
                    <div className="net-layer" key={i}>
                      <div className="net-label">{row.label}</div>
                      <div className={`net-bar ${row.bar}`}>{row.text}</div>
                      <div className="net-size">{row.size}</div>
                    </div>
                  )
                )}
              </div>
              <div style={{ marginTop: '1rem' }}>
                <div className="param-row">
                  <span className="param-key">Weight Init</span>
                  <span className="param-val green">Orthogonal</span>
                </div>
                <div className="param-row">
                  <span className="param-key">Execution</span>
                  <span className="param-val">Independent (no inter-agent comm)</span>
                </div>
              </div>
            </div>
          </div>

          <div className="arch-panel">
            <div className="arch-panel-header">
              <div className="arch-panel-dot green" />
              <div className="arch-panel-title">CENTRALIZED CRITIC (×1)</div>
            </div>
            <div className="arch-panel-body">
              <div className="network-diagram">
                {[
                  { label: 'Global State', bar: 'input', text: 'concat all 4 agents = 32-dim', size: '32' },
                  { label: '', arrow: true },
                  { label: 'Hidden 1', bar: 'h1', text: 'Linear(32→128) → ReLU', size: '128' },
                  { label: '', arrow: true },
                  { label: 'LayerNorm', bar: 'h2', text: 'LayerNorm(128)', size: '128' },
                  { label: '', arrow: true },
                  { label: 'Hidden 2', bar: 'h3', text: 'Linear(128→128) → ReLU', size: '128' },
                  { label: '', arrow: true },
                  { label: 'Value', bar: 'output', text: 'V(s_global)', size: '1' },
                ].map((row, i) =>
                  (row as any).arrow ? (
                    <div key={i} className="net-arrow">↓</div>
                  ) : (
                    <div className="net-layer" key={i}>
                      <div className="net-label">{row.label}</div>
                      <div className={`net-bar ${row.bar}`}>{row.text}</div>
                      <div className="net-size">{row.size}</div>
                    </div>
                  )
                )}
              </div>
              <div style={{ marginTop: '1rem' }}>
                <div className="param-row">
                  <span className="param-key">Loss</span>
                  <span className="param-val green">MSE</span>
                </div>
                <div className="param-row">
                  <span className="param-key">Training only</span>
                  <span className="param-val purple">Not used at inference</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Signal Control Architecture Diagram */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5, delay: 0.4 }}
        style={{ marginTop: '3rem' }}
      >
        <div className="section-label">Module Architecture</div>
        <h3 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: '0.5rem' }}>Signal Control Module Architecture</h3>
        <p className="section-desc" style={{ marginBottom: 0 }}>
          End-to-end architecture from data acquisition through state representation to the MAPPO training core.
        </p>
        <SignalArchDiagram />
      </motion.div>
    </section>
  )
}
