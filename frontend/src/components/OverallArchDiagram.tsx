export default function OverallArchDiagram() {
  return (
    <div className="oad-wrap">
      <div className="oad-title">Overall System Architecture</div>

      <div className="oad-body">

        {/* LEFT — Route + LSTGAN */}
        <div className="oad-col oad-col-left">
          <div className="oad-module">
            <div className="oad-module-title">Best Route Selection</div>
            <div className="oad-inner-row">
              <div className="oad-box">Edge Weight Computation</div>
              <div className="oad-arrow-r">→</div>
              <div className="oad-box">A* Algorithm</div>
            </div>
            <div className="oad-label-sm" style={{ marginTop: '0.4rem' }}>Prediction Metric</div>
          </div>

          <div className="oad-arrow-d" />

          <div className="oad-module">
            <div className="oad-module-title">LSTGAN</div>
            <div className="oad-inner-col">
              <div className="oad-box">Decoder</div>
              <div className="oad-inner-row" style={{ gap: '0.5rem' }}>
                <div className="oad-box oad-box-sm">Temporal Encoder</div>
                <div className="oad-box oad-box-sm">Spatial Encoder</div>
              </div>
            </div>
          </div>

          <div className="oad-arrow-d" />

          <div className="oad-module">
            <div className="oad-module-title">Simulation Environment</div>
            <div className="oad-inner-row">
              <div className="oad-box oad-box-sm">Road Network</div>
              <div className="oad-box oad-box-sm">Vehicles &amp; RSUs</div>
            </div>
          </div>

          <div className="oad-dataset">METR-LA Dataset</div>
        </div>

        {/* CENTER — Signal + Lane Change */}
        <div className="oad-col oad-col-center">
          {/* Traffic Signal Controller */}
          <div className="oad-module oad-module-accent">
            <div className="oad-module-title">Traffic Signal Controller</div>
            <div className="oad-sub-module">
              <div className="oad-sub-title">MAPPO</div>
              <div className="oad-inner-row" style={{ gap: '0.5rem', flexWrap: 'wrap' }}>
                <div className="oad-box oad-box-sm">PPO Update</div>
                <div className="oad-arrow-r">→</div>
                <div className="oad-box oad-box-sm">Actor/Critic Loss</div>
                <div className="oad-arrow-r">→</div>
                <div className="oad-box oad-box-sm">GAE</div>
              </div>
              <div className="oad-label-sm">Weight Update &nbsp;|&nbsp; Advantages, Returns</div>
              <div className="oad-inner-row" style={{ gap: '0.5rem', marginTop: '0.5rem' }}>
                <div className="oad-box oad-box-sm">Actor</div>
                <div className="oad-box oad-box-sm">Critic</div>
                <div className="oad-box oad-box-sm">Reward Computation</div>
              </div>
              <div className="oad-label-sm">Local State Obs &nbsp;|&nbsp; Global State Obs &nbsp;|&nbsp; Sensor Data</div>
            </div>
            <div className="oad-sub-module" style={{ marginTop: '0.75rem' }}>
              <div className="oad-sub-title">Simulation</div>
              <div className="oad-inner-row" style={{ gap: '0.5rem' }}>
                <div className="oad-box oad-box-sm">Signal Control Env</div>
                <div className="oad-box oad-box-sm">Route Generator</div>
              </div>
            </div>
          </div>

          <div className="oad-selected-lane">Selected Lane</div>
          <div className="oad-arrow-d" />

          {/* Lane Change Controller */}
          <div className="oad-module oad-module-accent">
            <div className="oad-module-title">Lane Change Controller</div>
            <div className="oad-sub-module">
              <div className="oad-sub-title">DRL (EV)</div>
              <div className="oad-inner-row" style={{ gap: '0.5rem', flexWrap: 'wrap' }}>
                <div className="oad-box oad-box-sm">PPO Update</div>
                <div className="oad-arrow-r">→</div>
                <div className="oad-box oad-box-sm">Policy Update</div>
                <div className="oad-arrow-r">→</div>
                <div className="oad-box oad-box-sm">Actor New (NN)</div>
              </div>
              <div className="oad-inner-row" style={{ gap: '0.5rem', marginTop: '0.5rem' }}>
                <div className="oad-box oad-box-sm">Actor Old (NN)</div>
                <div className="oad-arrow-r">↑ State Value</div>
                <div className="oad-box oad-box-sm">Critic (NN)</div>
              </div>
            </div>
          </div>
        </div>

        {/* RIGHT — V2X */}
        <div className="oad-col oad-col-right">
          <div className="oad-module">
            <div className="oad-module-title">V2X Communication</div>
            <div className="oad-inner-col">
              <div className="oad-box">
                Simulation<br />
                <span className="oad-box-detail">Speed, position, road, segment length</span>
              </div>
              <div className="oad-arrow-d-sm" />
              <div className="oad-box">Density Indicator Estimation</div>
              <div className="oad-arrow-d-sm" />
              <div className="oad-box">Periodic Parameter Update</div>
            </div>
          </div>
          <div className="oad-label-sm oad-param-label">QoS Parameter Update</div>
        </div>

      </div>
    </div>
  )
}
