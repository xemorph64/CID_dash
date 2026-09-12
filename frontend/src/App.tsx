import styles from './App.module.css'
import { CaseStrip } from './shell/CaseStrip'
import { FontSample } from './shell/FontSample'
import { Legend } from './shell/Legend'
import { QuestionRail } from './shell/QuestionRail'
import { TimeStrip } from './shell/TimeStrip'

// Layout regions per prd.md §5.5: case strip top, question rail left, the
// board full bleed in the middle, legend and time strip along the bottom.
function App() {
  return (
    <div className={styles.app}>
      <div className={styles.strip}>
        <CaseStrip />
      </div>
      <div className={styles.rail}>
        <QuestionRail />
      </div>
      <div className={styles.board}>
        <p className={styles.boardLabel}>The board — no case loaded, nothing to show yet.</p>
        <FontSample />
      </div>
      <div className={styles.legend}>
        <Legend />
      </div>
      <div className={styles.time}>
        <TimeStrip />
      </div>
    </div>
  )
}

export default App
