import styles from './Legend.module.css'

/** Fixed, always-on legend (prd.md §5.5). Teaches the evidence language on every screen. */
export function Legend() {
  return (
    <div className={styles.legend}>
      <span className={styles.item}>
        <span className={`${styles.swatch} ${styles.ink}`} aria-hidden="true" />
        Ink: on record.
      </span>
      <span className={styles.item}>
        <span className={`${styles.swatch} ${styles.dotted}`} aria-hidden="true" />
        Dotted: worked out from records.
      </span>
      <span className={styles.item}>
        <span className={`${styles.swatch} ${styles.pencil}`} aria-hidden="true" />
        Pencil: AI suggestion.
      </span>
      <span className={styles.item}>
        <span className={styles.stamp} aria-hidden="true" />
        Violet stamp: decided by an officer.
      </span>
    </div>
  )
}
