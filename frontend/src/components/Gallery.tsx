import { motion } from 'framer-motion'
import { useInView } from '../hooks/useInView'
import type { LightboxImg } from '../App'

import ss1 from '../assets/Screenshot 2026-04-04 102711.png'
import ss2 from '../assets/Screenshot 2026-04-04 102729.png'
import ss4 from '../assets/Screenshot 2026-04-04 102757.png'
import ss5 from '../assets/Screenshot 2026-04-04 102813.png'
import training from '../assets/ppo_training_progress.png'
import waImg from '../assets/IMG-20260405-WA0051.jpg'
import junctionVid from '../assets/VID-20260405-WA0024.mp4'

const images = [
  { src: training, caption: 'PPO Training Reward Curve', color: '#388bfd', span: true },
  { src: ss1, caption: 'EV lane-change simulation — multi-lane scenario', color: '#3fb950', span: false },
  { src: ss2, caption: 'Surrounding vehicle state observation', color: '#bc8cff', span: false },
  { src: ss4, caption: 'EV clearance path — signal preemption active', color: '#388bfd', span: false },
  { src: ss5, caption: 'Dense traffic evaluation run', color: '#e3b341', span: false },
  { src: waImg, caption: 'Cross-junction (+) simulation environment', color: '#3fb950', span: false },
]

interface Props { onOpen: (src: LightboxImg) => void }

export default function Gallery({ onOpen }: Props) {
  const [ref, inView] = useInView()

  return (
    <div className="gallery-inner" id="gallery" ref={ref}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5 }}
      >
        <div className="section-label">Simulation Output</div>
        <h2 className="section-title">Screenshots and Training Output</h2>
        <p className="section-desc">
          Screenshots and training curves captured from simulation runs, alongside
          a live demonstration of the cross-junction signal control environment.
        </p>
      </motion.div>

      {/* Video — cross junction demo */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={inView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.5, delay: 0.1 }}
        style={{ marginTop: '2rem' }}
      >
        <div className="video-wrapper">
          <video
            src={junctionVid}
            controls
            muted
            playsInline
            className="junction-video"
          />
          <div className="gallery-caption" style={{ borderTop: '1px solid var(--border)', padding: '0.75rem 1rem' }}>
            <div className="gallery-caption-dot" style={{ background: '#388bfd' }} />
            Cross-junction (+) MARL signal control — live simulation recording
          </div>
        </div>
      </motion.div>

      {/* Image grid */}
      <div className="gallery-grid" style={{ marginTop: '1.5rem' }}>
        {images.map((item, i) => (
          <motion.div
            key={i}
            className={`gallery-item${item.span ? ' span-2' : ''}`}
            initial={{ opacity: 0, y: 30 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.5, delay: 0.05 * i }}
            onClick={() => onOpen(item.src)}
          >
            <img src={item.src} alt={item.caption} />
            <div className="gallery-caption">
              <div className="gallery-caption-dot" style={{ background: item.color }} />
              {item.caption}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
