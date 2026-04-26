export default function SignalArchDiagram() {
  return (
    <div className="arch-diagram">
      <div className="arch-diagram-title">SIGNAL CONTROL MODULE ARCHITECTURE</div>

      {/* INPUT LAYER */}
      <div className="arch-layer">
        <div className="arch-layer-label">INPUT LAYER (DATA ACQUISITION)</div>
        <div className="arch-layer-body">
          <div className="arch-input-grid">
            <div className="arch-box">
              <div className="arch-box-title">
                <span className="arch-icon">&#9traffic;</span>
                Traffic State Collector
              </div>
              <ul className="arch-list">
                <li>Vehicle Count per Lane</li>
                <li>Queue Length</li>
                <li>Waiting Time</li>
                <li>Vehicle Speed</li>
              </ul>
            </div>
            <div className="arch-box">
              <div className="arch-box-title">V2X Interface</div>
              <ul className="arch-list">
                <li>Emergency Vehicle Detection</li>
                <li>Vehicle Position &amp; Priority</li>
                <li>RSU Inputs</li>
              </ul>
            </div>
            <div className="arch-box">
              <div className="arch-box-title">Sensor Interface</div>
              <ul className="arch-list">
                <li>Lane Occupancy</li>
                <li>Traffic Density</li>
                <li>Signal Phase Status</li>
              </ul>
            </div>
          </div>
          <div className="arch-arrow-down" />
          <div className="arch-vector-box dashed">RAW TRAFFIC STATE VECTOR</div>
        </div>
      </div>

      <div className="arch-arrow-down" />

      {/* STATE REPRESENTATION LAYER */}
      <div className="arch-layer">
        <div className="arch-layer-label">STATE REPRESENTATION LAYER</div>
        <div className="arch-layer-body">
          <div className="arch-state-grid">
            <div className="arch-box">
              <div className="arch-box-title">Local State Encoder</div>
              <ul className="arch-list"><li>Lane-Wise Features</li></ul>
            </div>
            <div className="arch-box arch-box-center">
              <div className="arch-box-title">Feature Normalization</div>
            </div>
            <div className="arch-box">
              <div className="arch-box-title">Global State Aggregator</div>
              <ul className="arch-list"><li>Network-Wide Traffic Context</li></ul>
            </div>
          </div>
          <div className="arch-arrow-down" />
          <div className="arch-vector-box solid">STATE VECTOR (S<sub>t</sub>)</div>
        </div>
      </div>

      <div className="arch-arrow-down" />

      {/* MAPPO CORE */}
      <div className="arch-layer arch-layer-dark">
        <div className="arch-layer-label">MULTI-AGENT PPO (MAPPO CORE)</div>
        <div className="arch-layer-body">
          <div className="arch-mappo-top">
            <div className="arch-box">
              <div className="arch-box-title">Actor Network</div>
              <ul className="arch-list"><li>Lane-Wise Features</li></ul>
            </div>
            <div className="arch-mappo-arrows">
              <div className="arch-arrow-lr">&#8596;</div>
            </div>
            <div className="arch-box">
              <div className="arch-box-title">Critic Network</div>
              <ul className="arch-list"><li>State Value V(s<sub>t</sub>)</li></ul>
            </div>
          </div>
          <div className="arch-arrow-down" />
          <div className="arch-vector-box solid arch-adv">Advantage Estimation</div>
          <div className="arch-arrow-down" />
          <div className="arch-mappo-bottom">
            <div className="arch-box">
              <div className="arch-box-title">Policy Update (PPO)</div>
              <ul className="arch-list">
                <li>Actor Critic Loss</li>
                <li>Reward Computation</li>
              </ul>
            </div>
            <div className="arch-mappo-arrows">
              <div className="arch-arrow-lr">&#8596;</div>
            </div>
            <div className="arch-box">
              <div className="arch-box-title">Critic Network (S<sub>t</sub>)</div>
              <ul className="arch-list"><li>State Value V(s<sub>t</sub>)</li></ul>
            </div>
          </div>
          <div className="arch-arrow-down" />
          <div className="arch-vector-box solid">STATE VECTOR (S<sub>t</sub>)</div>
        </div>
      </div>

      <div className="arch-arrow-down" />

      {/* ENVIRONMENT LAYER */}
      <div className="arch-env-grid">
        <div className="arch-box arch-box-env">
          <div className="arch-box-title">SIGNAL CONTROL ENV</div>
          <div className="arch-box-sub">Custom Simulation</div>
        </div>
        <div className="arch-box arch-box-env">
          <div className="arch-box-title">ROUTE GENERATION</div>
          <div className="arch-box-sub">External RSU Data</div>
        </div>
      </div>

      <div className="arch-arrow-down" />

      {/* STATE OUTPUT */}
      <div className="arch-state-output">
        <div className="arch-vector-box dashed arch-local">
          LOCAL STATE<br /><span className="arch-sub">(Partial S<sub>t</sub>)</span>
        </div>
        <div className="arch-vector-box solid arch-global">
          GLOBAL STATE<br /><span className="arch-sub">(S<sub>t</sub>)</span>
        </div>
      </div>
    </div>
  )
}
