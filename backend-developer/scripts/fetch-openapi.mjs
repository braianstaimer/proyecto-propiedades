#!/usr/bin/env node
// Hidrata static/openapi.json desde el backend vivo.
// Uso: OPENAPI_URL=http://localhost:8000/openapi.json node scripts/fetch-openapi.mjs

import { writeFileSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const TARGET = join(__dirname, '..', 'static', 'openapi.json')
const URL = process.env.OPENAPI_URL || 'http://localhost:8000/openapi.json'

console.log(`→ Fetching ${URL}`)
try {
  const res = await fetch(URL)
  if (!res.ok) {
    console.error(`✗ HTTP ${res.status}`)
    process.exit(1)
  }
  const spec = await res.json()
  writeFileSync(TARGET, JSON.stringify(spec, null, 2) + '\n', 'utf-8')
  console.log(`✓ Wrote ${TARGET}`)
  console.log(`  title=${spec.info?.title} version=${spec.info?.version}`)
  console.log(`  paths=${Object.keys(spec.paths || {}).length}`)
} catch (err) {
  console.error('✗', err.message || err)
  process.exit(1)
}
