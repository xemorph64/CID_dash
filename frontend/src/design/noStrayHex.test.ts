import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'

// architecture.md §8.1: the seven colours live only in tokens.css as CSS
// variables. Every other file must reference them via var(--token-name).
const SRC_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const TOKENS_FILE = path.join(SRC_DIR, 'design', 'tokens.css')
const HEX_COLOUR = /#[0-9a-fA-F]{8}\b|#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3,4}\b/

function allFiles(dir: string): string[] {
  return fs
    .readdirSync(dir, { recursive: true, encoding: 'utf-8' })
    .map((entry) => path.join(dir, entry))
    .filter((entry) => fs.statSync(entry).isFile())
}

describe('no stray hex colours outside tokens.css', () => {
  it('finds no hex colour literal in any file under src except tokens.css', () => {
    const offenders = allFiles(SRC_DIR)
      .filter((file) => file !== TOKENS_FILE)
      .filter((file) => HEX_COLOUR.test(fs.readFileSync(file, 'utf-8')))

    expect(offenders).toEqual([])
  })
})
