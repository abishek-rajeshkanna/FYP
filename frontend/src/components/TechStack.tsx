import { motion } from 'framer-motion'
import { useInView } from '../hooks/useInView'

const stack = [
  { name: 'PyTorch', color: '#f78166' },
  { name: 'PyGame', color: '#388bfd' },
  { name: 'NumPy', color: '#bc8cff' },
  { name: 'Pandas', color: '#e3b341' },
  { name: 'Matplotlib', color: '#388bfd' },
  { name: 'PPO', color: '#3fb950' },
  { name: 'MAPPO', color: '#bc8cff' },
  { name: 'GAE', color: '#f78166' },
  { name: 'CTDE', color: '#e3b341' },
  { name: 'Python 3.10+', color: '#388bfd' },
  { name: 'CUDA', color: '#3fb950' },
  { name: 'V2X / TraCI', color: '#f78166' },
]

export default function TechStack() {
  const [ref, inView] = useInView()

  return (
    <section className="section" ref={ref}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5 }}
      >
        <div className="section-label">Built With</div>
        <h2 className="section-title">Technology Stack</h2>
        <p className="section-desc">
          The full pipeline from simulation to training to evaluation.
        </p>
        <div className="tech-grid">
          {stack.map((t, i) => (
            <motion.div
              key={t.name}
              className="tech-pill"
              initial={{ opacity: 0, scale: 0.85 }}
              animate={inView ? { opacity: 1, scale: 1 } : {}}
              transition={{ duration: 0.3, delay: 0.03 * i }}
            >
              <div className="tech-pill-dot" style={{ background: t.color, boxShadow: `0 0 6px ${t.color}` }} />
              {t.name}
            </motion.div>
          ))}
        </div>
      </motion.div>
    </section>
  )
}
