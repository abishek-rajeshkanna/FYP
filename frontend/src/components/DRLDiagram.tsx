export default function DRLDiagram() {
  return (
    <div className="drl-diag">
      <div className="drl-diag-title">DRL Based Lane Change for EVs</div>
      <div className="drl-diag-grid">

        {/* Row 1: empty | state label | empty */}
        <div />
        <div className="drl-state-label">
          State<br /><span className="drl-sub">(Position, Speed)</span>
        </div>
        <div />

        {/* Row 2: empty | arrow down | empty */}
        <div />
        <div className="drl-arrow-center">↓</div>
        <div />

        {/* Row 3: PPO Clipping --Update--> Actor New --> Actor Old */}
        <div className="drl-node">PPO Clipping</div>
        <div className="drl-node drl-node-main">
          Actor New<br /><span className="drl-sub">(Neural Network)</span>
        </div>
        <div className="drl-node">
          Actor Old<br /><span className="drl-sub">(Neural Network)</span>
        </div>

        {/* Row 4: arrow up | arrow down | empty */}
        <div className="drl-arrow-center">↑</div>
        <div className="drl-arrow-center">↓</div>
        <div />

        {/* Row 5: Critic | Action label | empty */}
        <div className="drl-node">
          Critic<br /><span className="drl-sub">(Neural Network)</span>
        </div>
        <div className="drl-action-label">
          Action (Decision)<br /><span className="drl-sub">[-1, 0, 1]</span>
        </div>
        <div />

        {/* Row 6: arrow up | arrow down | empty */}
        <div className="drl-arrow-center">↑</div>
        <div className="drl-arrow-center">↓</div>
        <div />

        {/* Row 7: Reward <-- Simulation Env | empty */}
        <div className="drl-node">Reward</div>
        <div className="drl-node drl-node-env">
          Simulation Env<br /><span className="drl-sub">(New State)</span>
        </div>
        <div />

      </div>

      {/* Horizontal arrow labels */}
      <div className="drl-h-arrows">
        <div className="drl-h-arrow drl-h-top">
          <span className="drl-h-line" />
          <span className="drl-h-label">Update</span>
          <span className="drl-h-line" />
        </div>
        <div className="drl-h-arrow drl-h-bottom">
          <span className="drl-h-line" />
          <span className="drl-h-label">←</span>
          <span className="drl-h-line" />
        </div>
      </div>
    </div>
  )
}
