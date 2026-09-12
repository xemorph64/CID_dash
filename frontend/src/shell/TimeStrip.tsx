import styles from './TimeStrip.module.css'

/**
 * Inert placeholder for the bottom time-strip region (prd.md §5.5).
 * No fake activity data — replay lands in M8.
 */
export function TimeStrip() {
  return (
    <div className={styles.strip}>
      Replay
      <span className={styles.bar} aria-hidden="true" />
    </div>
  )
}
