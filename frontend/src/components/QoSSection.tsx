import { motion } from 'framer-motion'
import { useInView } from '../hooks/useInView'

const densityLevels = [
  {
    label: 'Low Density',
    range: 'β ≤ 3',
    color: 'green',
    params: [
      { key: 'R (comm. range)', val: 'R_max' },
      { key: 'σ (carrier sense)', val: '0.25  →  R_c = 2R' },
      { key: 'λ (packet rate)', val: '10 − β  packets/s' },
    ],
    desc: 'Full communication range is maintained. Carrier sensing extends to 2R to minimize hidden terminal collisions in sparse traffic.',
  },
  {
    label: 'Medium Density',
    range: '3 < β ≤ 7',
    color: 'blue',
    params: [
      { key: 'R (comm. range)', val: 'R_min + β·ΔR/10' },
      { key: 'σ (carrier sense)', val: '0.5  →  R_c ∈ [R, 2R]' },
      { key: 'λ (packet rate)', val: '10 − β  packets/s' },
    ],
    desc: 'Communication range scales linearly with density level. Carrier sensing is balanced to reduce channel load while maintaining coverage.',
  },
  {
    label: 'High Density',
    range: 'β > 7',
    color: 'orange',
    params: [
      { key: 'R (comm. range)', val: 'R_min + β·ΔR/10' },
      { key: 'σ (carrier sense)', val: '1.0  →  R_c = R' },
      { key: 'λ (packet rate)', val: '10 − β  packets/s' },
    ],
    desc: 'Communication and carrier sensing ranges are reduced to R to minimize interference. Packet rate is lowered to prevent channel saturation.',
  },
]

const cwRule = {
  condition: 'T_EM > 1.2 × T\'_EM',
  action: 'W_c = min(W_c + 16, 120)',
  desc: 'When emergency message delay increases by more than 20% over the previous measurement, the contention window is expanded to reduce packet collisions.',
}

const algoSteps = [
  {
    num: '01',
    title: 'Vehicular Density Estimation',
    desc: 'Every 10 control channel intervals (CCI), the EV computes current vehicular density ρ from average speed using the speed-density inverse relationship. A density level β ∈ [0,9] is derived as β = ⌊(ρ/ρ_max) × 10⌋.',
    code: `ρ = F / v
β = ⌊(ρ / ρ_max) × 10⌋
λ = 10 − β`,
  },
  {
    num: '02',
    title: 'Communication Range Adaptation',
    desc: 'R is adjusted within [R_min, R_max] proportional to β. At high density, reducing R limits the number of vehicles competing for the channel, improving per-vehicle throughput.',
    code: `R = R_min + β × (R_max − R_min) / 10`,
  },
  {
    num: '03',
    title: 'Carrier Sensing Range Control',
    desc: 'The carrier sensing parameter σ controls R_c relative to R. Reducing R_c at high density decreases waiting time per vehicle, at the cost of increased hidden terminal probability — mitigated by simultaneous R reduction.',
    code: `σ = 1.0   (high)   → R_c = R
σ = 0.5   (medium) → R_c ∈ [R, 2R]
σ = 0.25  (low)    → R_c = 2R`,
  },
  {
    num: '04',
    title: 'Contention Window Adjustment',
    desc: 'The contention window W_c is dynamically expanded when EM delay increases beyond a 20% threshold over the previous measurement. This reduces the probability of simultaneous transmissions causing packet collisions.',
    code: `if T_EM > 1.2 × T'_EM:
    W_c = min(W_c + 16, 120)`,
  },
  {
    num: '05',
    title: 'Emergency Message Broadcast',
    desc: 'After parameter updates, all five V2X message types are broadcast. RSUs relay Msg 2 over an extended range so that AVs further ahead can initiate MLC in advance, reducing EV blocking time.',
    code: `EM ← {Msg1, Msg2, Msg3, Msg4, Msg5}
Broadcast(EM)`,
  },
]

export default function QoSSection() {
  const [ref, inView] = useInView()

  return (
    <section className="section" id="qos" ref={ref}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5 }}
      >
        <div className="section-label">Module 3</div>
        <h2 className="section-title">QoS-V2X — Adaptive Network Parameter Control</h2>
        <p className="section-desc">
          Both the DRL lane-change and MARL signal models depend on reliable V2X emergency
          message delivery. The QoS-V2X algorithm dynamically adjusts communication range,
          carrier sensing range, packet rate, and contention window based on real-time
          vehicular density to maintain packet reception rate and minimize EM delay.
        </p>
      </motion.div>

      {/* Density-based parameter table */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5, delay: 0.15 }}
        style={{ marginTop: '3rem' }}
      >
        <div className="section-label">Density-Adaptive Parameters</div>
        <div className="qos-density-grid">
          {densityLevels.map((d, i) => (
            <motion.div
              key={d.label}
              className={`qos-density-card border-${d.color}`}
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.4, delay: 0.2 + i * 0.1 }}
            >
              <div className="qos-density-header">
                <div className={`qos-density-dot ${d.color}`} />
                <div>
                  <div className="qos-density-label">{d.label}</div>
                  <div className={`qos-density-range ${d.color}`}>{d.range}</div>
                </div>
              </div>
              <div className="params-list" style={{ marginBottom: '0.75rem' }}>
                {d.params.map(p => (
                  <div className="param-row" key={p.key}>
                    <span className="param-key">{p.key}</span>
                    <span className={`param-val ${d.color}`}>{p.val}</span>
                  </div>
                ))}
              </div>
              <div className="qos-density-desc">{d.desc}</div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* CW rule */}
      <motion.div
        className="qos-cw-box"
        initial={{ opacity: 0, y: 20 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5, delay: 0.35 }}
      >
        <div className="qos-cw-title">Contention Window Dynamic Rule</div>
        <div className="qos-cw-row">
          <div className="qos-cw-item">
            <div className="qos-cw-item-label">Trigger Condition</div>
            <div className="flow-code" style={{ marginTop: '0.4rem' }}>
              <span style={{ color: 'var(--orange)' }}>{cwRule.condition}</span>
            </div>
          </div>
          <div className="qos-cw-arrow">→</div>
          <div className="qos-cw-item">
            <div className="qos-cw-item-label">Action</div>
            <div className="flow-code" style={{ marginTop: '0.4rem' }}>
              <span style={{ color: 'var(--green)' }}>{cwRule.action}</span>
            </div>
          </div>
        </div>
        <div className="qos-density-desc" style={{ marginTop: '0.75rem' }}>{cwRule.desc}</div>
      </motion.div>

      {/* Algorithm steps */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5, delay: 0.4 }}
        style={{ marginTop: '3.5rem' }}
      >
        <div className="section-label">Algorithm Walkthrough</div>
        <h3 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: '0.5rem' }}>QoS-V2X Execution per CCI Cycle</h3>
        <p className="section-desc" style={{ marginBottom: 0 }}>
          Executed every 10 control channel intervals by the EV, AVs, and RSUs simultaneously.
        </p>
        <div className="training-flow" style={{ marginTop: '2rem' }}>
          {algoSteps.map((s) => (
            <div className="flow-step" key={s.num}>
              <div className="flow-num">{s.num}</div>
              <div className="flow-content">
                <div className="flow-title">{s.title}</div>
                <div className="flow-desc">{s.desc}</div>
                <div className="flow-code">{s.code}</div>
              </div>
            </div>
          ))}
        </div>
      </motion.div>

      {/* V2X communication flow */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5, delay: 0.5 }}
        style={{ marginTop: '3.5rem' }}
      >
        <div className="section-label">V2X Communication Flow</div>
        <h3 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: '0.5rem' }}>Emergency Message Propagation Sequence</h3>
        <p className="section-desc" style={{ marginBottom: 0 }}>
          The sequence of events triggered when an emergency vehicle enters the network and propagates its presence to surrounding infrastructure and vehicles.
        </p>
        <div className="v2x-flow" style={{ marginTop: '2rem' }}>
          {[
            { actor: 'EMV', color: 'orange', label: 'EMV Broadcasts', desc: 'The emergency vehicle transmits an emergency message containing its position, speed, lane state, and lane-change status to all nodes within its communication range.' },
            { actor: 'AV', color: 'blue', label: 'AV Receives', desc: 'Autonomous vehicles within range receive the emergency message and parse the EV state. The lane-change state flag (state_LC) is checked to determine whether the EV is currently executing a manoeuvre.' },
            { actor: 'AV', color: 'blue', label: 'AV Performs Cooperative Yield', desc: 'When state_LC = 0, blocking AVs execute the Mobility-Aware Lane Change (MLC) algorithm — selecting the adjacent lane with sufficient gap and lower density to clear the path for the EV.' },
            { actor: 'AV', color: 'blue', label: 'AV Sends Response', desc: 'Each AV broadcasts its updated state (lateral position, longitudinal velocity, acceleration, and distance to EV) back to the RSU, enabling the infrastructure to maintain a current knowledge base of the local traffic.' },
            { actor: 'RSU', color: 'green', label: 'RSU Detects Transition', desc: 'The RSU monitors incoming AV state messages and detects lane-change transitions. It aggregates the states of all potential AV neighbors within its coverage area into a centralized knowledge base.' },
            { actor: 'RSU', color: 'green', label: 'RSU Informs Vehicles', desc: 'The RSU rebroadcasts the emergency message over an extended range, enabling AVs further ahead to initiate cooperative yielding in advance — reducing the blocking time experienced by the EV.' },
            { actor: 'RSU', color: 'green', label: 'RSU Communicates with Other RSUs', desc: 'The RSU forwards the aggregated neighbor state information to the EV, which uses it as input to the DRL policy for lane-change decision-making. Adjacent RSUs coordinate to ensure seamless coverage across the road network.' },
          ].map((step, i) => (
            <div className="flow-step" key={step.label}>
              <div className={`flow-num v2x-actor-${step.color}`}>{step.actor}</div>
              <div className="flow-content">
                <div className="flow-title">{step.label}</div>
                <div className="flow-desc">{step.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    </section>
  )
}
