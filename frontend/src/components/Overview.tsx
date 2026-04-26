import { motion } from 'framer-motion'
import { useInView } from '../hooks/useInView'
import { Cpu, Network, Activity, GitBranch } from 'lucide-react'
import SignalArchDiagram from './SignalArchDiagram'
import OverallArchDiagram from './OverallArchDiagram'

const cards = [
  {
    icon: <Cpu size={20} />,
    color: 'blue',
    title: 'DRL-PPO Lane Change',
    desc: 'A Proximal Policy Optimization agent trained to control Emergency Vehicle lane-change decisions, selecting from three lateral actions at each decision interval based on a 29-dimensional state observation.',
  },
  {
    icon: <Network size={20} />,
    color: 'green',
    title: 'MARL Signal Control',
    desc: 'Four independent actor networks operating under Centralized Training, Decentralized Execution (CTDE) to coordinate traffic signal phases at a cross-junction, with EV proximity incorporated into each agent\'s local state.',
  },
  {
    icon: <Activity size={20} />,
    color: 'purple',
    title: 'Custom Simulation Environments',
    desc: 'Both models are trained and evaluated through custom simulation environments built with PyGame, with dynamic traffic generation to improve policy generalization across varying traffic conditions.',
  },
  {
    icon: <GitBranch size={20} />,
    color: 'orange',
    title: 'Integrated Pipeline',
    desc: 'The trained PPO model is loaded into the MARL training loop, enabling joint optimization where signal agents learn to coordinate with the EV lane-change policy in a shared environment.',
  },
]

export default function Overview() {
  const [ref, inView] = useInView()

  return (
    <section className="section" id="overview" ref={ref}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5 }}
      >
        <div className="section-label">System Overview</div>
        <h2 className="section-title">Project Architecture</h2>
        <p className="section-desc">
          The system addresses urban emergency vehicle preemption through two complementary
          reinforcement learning models operating within custom simulation environments.
        </p>
      </motion.div>

      <div className="overview-grid">
        {cards.map((c, i) => (
          <motion.div
            className="overview-card"
            key={c.title}
            initial={{ opacity: 0, y: 30 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.5, delay: 0.1 + i * 0.1 }}
          >
            <div className={`card-icon ${c.color}`}>{c.icon}</div>
            <div className="card-title">{c.title}</div>
            <div className="card-desc">{c.desc}</div>
          </motion.div>
        ))}
      </div>

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5, delay: 0.5 }}
        style={{ marginTop: '3rem' }}
      >
        <div className="section-label">Module Architecture</div>
        <h3 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: '0.5rem' }}>Overall Architecture</h3>
        <OverallArchDiagram />
      </motion.div>
    </section>
  )
}

