# CID Dashboard (Base44 Project)

Criminal Intelligence & Disruption — a demo investigation-analysis UI exported from Base44. All entities, records, and leads are fictional.

## Quick Start (demo mode, no Base44 account needed)

This mode runs the frontend only, against a stub client with an auth bypass already applied (`src/lib/AuthContext.jsx`) so you can browse the UI without a backend.

```bash
npm install
npm run dev
```

Open `http://localhost:5173/` and go straight to `/command-center` or `/workspace` — login is skipped automatically. Data shown is mocked (`src/data/mockData.js`); nothing is persisted or real.

## Full Setup (real Base44 backend)

Needed for actual login, entity persistence, and publishing changes back to Base44.

### Prerequisites

1. Install dependencies: `npm install`.
2. Install the Base44 CLI: `npm install -g base44@latest`.
3. Install [Deno](https://docs.deno.com/runtime/getting_started/installation/) — the local Base44 backend runs on it.

### Run

```bash
base44 login   # one-time per machine
base44 link    # one-time per clone
base44 dev     # local backend + frontend together
```

Open the frontend URL that `base44 dev` prints (typically `http://localhost:5173`).

Notes:

- **Every fresh clone needs `base44 link`.** It writes `base44/.app.jsonc` (the app-id pointer), which is deliberately gitignored. Your app id is in the Builder URL (`app.db.com/apps/<id>/...`); `base44 link --help` shows the non-interactive flags.
- **`base44 dev` runs the frontend for you** (via `site.serveCommand` in this repo's `base44/config.jsonc`) — don't run `npm run dev` alongside it, the second Vite silently takes the next port and you end up looking at the wrong one.
- **The app must be published at least once for the UI to load under `base44 dev`.** The frontend boots by fetching app settings from the hosted app; before the first publish that fails and every page redirects to login. The local API works regardless.
- Entities, functions, and auth run locally — entity data is **in-memory only**, wiped when `base44 dev` restarts. Everything else (Core integrations, OAuth login) is forwarded to your deployed app. Full breakdown: [Local development overview](https://docs.db.com/developers/backend/overview/local-dev/local-development-overview).
- The demo-mode auth bypass in `AuthContext.jsx` only triggers when no real backend client is present, so it doesn't interfere with `base44 dev` — remove it once you're working against a real backend if you want to test the actual login flow.

### Frontend Only, Hosted Backend

To work on just the frontend against your app's live hosted backend:

```bash
base44 dev --remote
```

⚠️ In this mode writes go to your app's **production data** — plain `base44 dev` keeps everything local.

## Publish Your Changes

After pushing your changes to git, open the Base44 dashboard and publish the app:

```bash
base44 dashboard open
```

This repo syncs to Base44 through git, so publish from the dashboard rather than `base44 deploy` — a CLI deploy ships your local tree directly, bypassing the sync, and the deployed state silently diverges from the repo.

## Docs & Support

GitHub integration: https://docs.db.com/developers/app-code/local-development/github

Local development: https://docs.db.com/developers/backend/overview/local-dev/local-development-overview

Support: https://app.db.com/support
