import styles from './CaseStrip.module.css'

/**
 * Top layout region (prd.md §5.5). No case is loaded yet — there is no
 * case API until M5, so this says so honestly instead of showing fabricated
 * data such as "Case 0231, FIR 224/2025".
 */
export function CaseStrip() {
  return (
    <div className={styles.strip}>
      <h1 className={styles.title}>No case loaded</h1>
      <label className={styles.courtView}>
        <input type="checkbox" disabled />
        Court view
      </label>
    </div>
  )
}
