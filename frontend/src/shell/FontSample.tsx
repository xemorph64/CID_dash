import styles from './FontSample.module.css'

/**
 * Proves both type voices load and render Devanagari (M0 acceptance check,
 * prd.md §5.4): Anek for C.I.D. speaking, Tiro for the record speaking.
 */
export function FontSample() {
  return (
    <div className={styles.sample}>
      <span className={styles.anek}>Mohammad Ali</span>
      <span className={styles.tiro}>मोहम्मद अली</span>
    </div>
  )
}
