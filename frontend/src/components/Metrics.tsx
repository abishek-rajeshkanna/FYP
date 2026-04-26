import { motion } from 'framer-motion'
import { useInView } from '../hooks/useInView'

const metrics = [
  { val: '85%', label: 'Success Rate', sub: 'DRL-PPO evaluation', color: 'green' },
  { val: '11.2', label: 'Avg Speed (m/s)', sub: 'vs 7.4 baseline', color: 'blue' },
  { val: '2.1x', label: 'Faster Travel', sub: 'PPO vs no lane change', color: 'purple' },
  { val: '6', label: 'Signal Agents', sub: 'CTDE coordination', color: 'orange' },
  { val: '1000', label: 'Training Episodes', sub: 'per model', color: 'blue' },
  { val: '128', label: 'Rollout Steps', sub: 'per PPO epoch', color: 'purple' },
]

const compareRows = [
  { method: 'DRL-PPO (Ours)', speed: '11.2 m/s', travel: '~420s', changes: '8–14', safety: '91%', highlight: true },
  { method: 'No Lane Change', speed: '7.4 m/s', travel: '~880s', changes: '0', safety: '72%', highlight: false },
  { method: 'Random Policy', speed: '6.1 m/s', travel: '>1000s', changes: 'random', safety: '55%', highlight: false },
]

export default function Metrics() {
  const [ref, inView] = useInView()

  return (
    <section className="section" id="metrics" ref={ref}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5 }}
      >
        <div className="section-label">Performance Results</div>
        <h2 className="section-title">Evaluation Metrics</h2>
        <p className="section-desc">
          Both models evaluated over 20 episodes in SUMO. DRL-PPO compared against a
          no-lane-change baseline and random policy.
        </p>
      </motion.div>

      <div className="metrics-grid">
        {metrics.map((m, i) => (
          <motion.div
            key={m.label}
            className={`metric-card ${m.color}`}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={inView ? { opacity: 1, scale: 1 } : {}}
            transition={{ duration: 0.4, delay: 0.05 * i }}
          >
            <div className={`metric-val ${m.color}`}>{m.val}</div>
            <div className="metric-label">{m.label}</div>
            <div className="metric-sub">{m.sub}</div>
          </motion.div>
        ))}
      </div>

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5, delay: 0.3 }}
        style={{ marginTop: '3rem' }}
      >
        <div className="section-label">Comparison</div>
        <h3 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: '1rem' }}>
          DRL-PPO vs Baselines
        </h3>
        <div style={{ overflowX: 'auto', borderRadius: '12px', border: '1px solid var(--border)' }}>
          <table className="compare-table">
            <thead>
              <tr>
                <th>Method</th>
                <th>Avg Speed</th>
                <th>Travel Time</th>
                <th>Lane Changes</th>
                <th>Safety Rate</th>
              </tr>
            </thead>
            <tbody>
              {compareRows.map(r => (
                <tr key={r.method} className={r.highlight ? 'highlight' : ''}>
                  <td>{r.method}</td>
                  <td>
                    <span className={`tag ${r.highlight ? 'good' : 'bad'}`}>{r.speed}</span>
                  </td>
                  <td>
                    <span className={`tag ${r.highlight ? 'good' : 'bad'}`}>{r.travel}</span>
                  </td>
                  <td>{r.changes}</td>
                  <td>
                    <span className={`tag ${r.highlight ? 'good' : r.method === 'No Lane Change' ? 'neutral' : 'bad'}`}>
                      {r.safety}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>
    </section>
  )
}
