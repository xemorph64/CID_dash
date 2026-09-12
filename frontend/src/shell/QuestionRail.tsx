import styles from './QuestionRail.module.css'

// prd.md §5.6.2 — the five questions, fixed order and wording. This
// vocabulary must never be paraphrased.
const QUESTIONS = [
  "Who's connected?",
  'Where did the money go?',
  'Who holds it together?',
  'When did it happen?',
  'Where were they?',
] as const

/** Left rail (prd.md §5.5). All five inert at M0 — no lens exists yet. */
export function QuestionRail() {
  return (
    <nav className={styles.rail} aria-label="Questions">
      {QUESTIONS.map((question) => (
        <button key={question} type="button" className={styles.question} disabled>
          {question}
        </button>
      ))}
    </nav>
  )
}
