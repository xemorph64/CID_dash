# C.I.D. Prototype — Product Requirements (`prd.md`)

> **Who reads this:** the team, and Claude as the coding agent.
> **Source of truth:** `docs/CID_Master_Project_Document_v2.0.md` (the *master*). This file turns the master into a buildable prototype. If this file conflicts with the master, the master wins — write the conflict into `docs/NOTES.md` and ask; never resolve it silently.
> **Companions:** `architecture.md` (how it is built) · `implementation.md` (in what order, with what tests).

**Labels used here**

| Label | Meaning |
|---|---|
| `DECIDED` | Decided in the master (§31 decision IDs cited) |
| `PROTOTYPE DEFAULT` | An open question in the master, answered *for this prototype only*. Listed in §10 for the team to confirm. |
| `STRETCH` | Build only after everything else in its milestone passes |

---

## 1. What we are building

A working C.I.D. prototype that runs on one laptop, on a synthetic world of FIRs, call records, bank transactions, company records and vehicle records, and proves the whole C.I.D. loop end to end:

```
scattered records → one identity → a network → an AI lead → the receipts behind it → an officer's decision → a court-ready case packet
```

The prototype has two jobs:

1. **Prove the core works** — entity resolution, the evidence-linked graph, key players, AI leads with explanations, lead-vs-evidence separation. Master tiers: Core, plus a few Advanced features (§04.4).
2. **Make it feel effortless for a police officer.** Nobody should need training to understand the screen. This is the "Case Board" experience in §5.

---

## 2. Goals and non-goals

### Goals

| ID | Goal |
|---|---|
| G1 | Messy, cross-script name variants of one person collapse into one identity with visible confidence; two different people with the same name stay apart. |
| G2 | Every line on the network opens the exact record(s) behind it. |
| G3 | Records, computed links and AI suggestions look different everywhere, and "Court view" hides everything that is not on record in one click. |
| G4 | C.I.D. ranks a short list of leads and explains each one in plain language with its receipts. |
| G5 | An officer can simulate cutting key players and see the network fall apart. |
| G6 | Every access and decision is logged in a tamper-evident audit chain that can be verified on screen. |
| G7 | The prototype reports honest metrics on the synthetic world (where ground truth is known). |

### Non-goals (do not build)

Real data of any kind · national scale · Kafka / Flink streaming · TigerGraph · federated learning / differential privacy · multi-teacher distillation · chat / LLM question answering · facial recognition · production-grade auth (demo users only) · mobile layout (desktop-first; must not break at 1280 px wide).

---

## 3. Users in the prototype

All users are fictional demo accounts.

| Role | Demo user | Does in the demo | Cannot |
|---|---|---|---|
| Investigating Officer (IO) | `io.patil` | Opens leads for assigned case 0231, explores the board, erases or pins AI suggestions, builds the case packet | See cases not assigned to them; split identities |
| Crime analyst | `analyst.khan` | Explores networks across assigned cases, runs Cut | Export case packets |
| Supervisor / ER reviewer | `supervisor.desai` | Decides review-queue merges, approves proactive leads outside a case | — |
| Prosecutor | `prosecutor.rao` | Opens case packets; board is locked to Court view | See AI suggestions |
| Auditor | `auditor.iyer` | Views and verifies the audit chain | See case content |

Roles map to master §07. Permissions are enforced by the API, not just hidden in the UI (master G-06).

---

## 4. The demo story — the whole product in six minutes

This story is the acceptance test for the product. Every beat must work on the seeded synthetic world, in this order, without touching a terminal.

| # | Beat | What the audience sees | Master |
|---|---|---|---|
| 1 | **Today's leads** | Log in as `io.patil`. No dashboard of numbers — five plain sentences, ranked. Top: *"Money moved through two new companies in six days."* | F-08, §17.7 |
| 2 | **One person, four records** | Open the lead. Four record cards — *Mohammad Ali* (FIR), *Mohd Ali* (bank KYC), *Md. Ali* (phone registration), *मोहम्मद अली* (company register) — slide together into one person. The card stack shows "4 records". Fan it out: chips say *same phone*, *same birth date*, *sounds alike*. | F-05, §11 |
| 3 | **The trap** | Search "Raj Kumar": two people, kept apart. The review queue shows why — similar name, different birth date and phone. The supervisor stamped them "Different people." | D-06, §11.9 |
| 4 | **Where did the money go?** | Switch to the money question. The same network flows left to right like a river, each hop labelled with how much stayed behind (<10%). | F-11 |
| 5 | **Show me the receipts** | Click the chain and choose *Why?* The drawer opens: the FIR sentence highlighted, the three transactions, the company registration (41 days old). Below: "If we remove these 6 links, the model's concern drops from 0.94 to 0.21." And: *What this does not show.* | F-01, F-09, §18 |
| 6 | **Pencil is not ink** | A grey pencil line appears: the AI suggests Person A may know Person D. Try to make it a fact — you can't click it into ink. You can only *Pin a record* (the system refuses when no record states the link) or *Erase* it with a reason. Erasing leaves a violet stamp with the officer's name. | F-02, F-03, §19.4 |
| 7 | **Who holds it together?** | Switch to the key-player question. The quiet name in the middle — Person A, only 3 direct links — matters most. Choose *Cut*; the suggested pair is marked; confirm. The network drifts apart into three islands: *"Splits into 3 groups. The largest keeps 38% of members."* A line below: *Shows structure only — not who would take over.* | F-04, F-07, C-10 |
| 8 | **Replay** | Press play on the time strip. The network grows through 2025 like a time-lapse. | F-13 |
| 9 | **Court view and the packet** | Flip *Court view*: every pencil line vanishes; only ink remains. *Build case packet* → three sections (on record / worked out / AI suggestions) with hashes. Open the audit page: "Audit chain verified — 1,284 entries, no gaps." | F-12, G-05, G-15 |

---

## 5. Experience design — "The Case Board"

### 5.1 The idea

> **C.I.D. looks and behaves like an investigator's desk. Records write in blue ink. The AI writes in pencil. Only an officer can stamp.**

Every tool on screen is something a police officer already understands from paper work: ink, pencil, rubber stamps, a highlighter, scissors, and a file of receipts. There is no new visual language to learn. The evidence model from the master (§19) *is* the visual language.

### 5.2 What we are deliberately not doing

| The usual crime-analytics UI | Why it fails here | What C.I.D. does instead |
|---|---|---|
| Dark "cyber" theme, neon glow, red threat colours | Looks like a movie; paints people as threats; tiring on long shifts | A cool grey desk with ink, pencil and stamp marks |
| A giant force-directed hairball | Nobody can read it; everything looks connected (master C-06) | Start small (one case, two steps out), expand on request, bundle crowds into "+18 calls" |
| KPI cards and charts on the home page | Numbers without a next action | Five ranked leads written as sentences |
| Twenty menu items | Training required | Five questions and three verbs |
| One colour for every link | Guesses look like facts | Ink, dotted ink, pencil — different on every screen |
| Risk shown as red percentages | "Risk = 94%" reads as guilt | Highlighter means "look here"; confidence shown in words |

### 5.3 Six rules of the board

1. **Three hands, three marks.** The records write in ink. C.I.D. works things out in dotted ink. The AI suggests in pencil. An officer decides with a violet stamp. No mark is ever drawn in another hand's style.
2. **Five questions, not menus.** The left rail asks the investigator's own questions (see 5.6.2). Each question re-arranges the *same* network; entities glide to new places so the eye never loses them.
3. **Three verbs on everything.** Any person, phone, account or company supports *Show who else*, *Why?* and *Cut*. Pencil lines add *Pin a record* and *Erase*. That is the whole interaction vocabulary.
4. **Every screen explains itself.** A caption sentence under the case strip always describes what is on screen, built from counts — no AI text. Example: *"14 people, 5 companies and 9 accounts within two steps of FIR 224/2025. 3 lines are AI suggestions."*
5. **Never paint a person red.** Attention is a highlighter stroke — "look here" — not a threat colour. Red is used only for scissors and cut marks, and for system errors.
6. **Nothing hidden, nothing faked.** Low-confidence items are drawn faint, never removed. Court view is one switch. Cell-tower places are drawn as fuzzy circles, never pins (master D-20).

### 5.4 Visual language

**Palette** — seven colours, each with one job:

| Name | Hex | Job |
|---|---|---|
| Desk | `#E9EDEB` | Canvas background — a cool record-room grey, never cream |
| Sheet | `#FAFBF9` | Drawers, record sheets, lead rows — paper laid on the desk |
| Blue ink | `#1D2B5C` | Text, and every documented link and entity outline |
| Graphite | `#7D828A` | AI suggestions (pencil), faint and secondary text |
| Stamp violet | `#5A3D8F` | Human decisions only: stamps, reviewer marks, audit |
| Highlighter | `#D9EE4A` | "Look here": highlighted record spans, entities in the open lead (used at ~55% opacity, multiply blend) |
| Cut red | `#B3362B` | Scissors, cut marks, destructive confirmations, errors |

Hairlines and dividers use Blue ink at 12% opacity. No gradients. No drop shadows except sheets lifting 1 px off the desk.

**Type** — two families, two voices. Both must be bundled locally (no font CDN).

| Family | Voice | Used for |
|---|---|---|
| **Anek** (Anek Latin + Anek Devanagari + Anek Tamil + Anek Bangla; Ek Type) | C.I.D. speaking | All interface text, captions, buttons, labels |
| **Tiro Devanagari Hindi** (Latin + Devanagari; Tiro Typeworks) | The record speaking | Record excerpts, names *as written in the source*, receipts |

Rule: if the text is a quotation from a source record, it is set in Tiro (Tamil and Bengali record text falls back to the matching Anek script, since Tiro covers Latin and Devanagari). Everything C.I.D. says is set in Anek. Anek was chosen because C.I.D. must show names in several Indian scripts in one consistent face — a core part of the entity-resolution story.

Type scale (1.25 ratio): 13 · 16 · 20 · 25 · 31 px. Body 16/24. Sentence case everywhere. No all-caps labels, no monospace. IDs use Anek with tabular figures.

**Entity shapes** — shape and a text label carry the type, never colour alone:

| Entity | Shape (Cytoscape) | Label |
|---|---|---|
| Person | `ellipse` | Initials inside, name below |
| Organization | `rectangle` | Name |
| BankAccount | `round-rectangle` | "₹" + last 4 of hash |
| PhoneNumber | `round-tag` | Last 4 of hash |
| Vehicle | `barrel` | Registration (synthetic) |
| Location (cell tower) | Large translucent circle, radius = footprint | Tower name |
| Location (point) | `round-diamond` | Place name |
| Event (FIR / arrest) | `cut-rectangle` (a page with a clipped corner) | "FIR 224/2025" |
| Device | `hexagon` | Last 4 of IMEI |

**Link styles** — the core of the design:

| Evidence class | Name on screen | Style | Detail |
|---|---|---|---|
| DOCUMENTED | **Ink** — "on record" | Solid Blue ink | Width 1.5–4.5 px by number of supporting records |
| DERIVED | **Dotted ink** — "worked out from records" | Dotted Blue ink, 2 px | e.g., co-presence, person-level calls |
| INFERRED | **Pencil** — "AI suggestion" | Graphite, 1.5 px, 80% opacity, slightly wavering curve, fine grain dash | Small "AI" tag at midpoint |
| Erased suggestion | — | Hidden; visible only with "Show erased" | Violet stamp on hover |

The pencil waver is a stable per-edge random bend (`unbundled-bezier`, seeded by edge ID) plus a dash pattern of `[9, 2]`. It must look hand-drawn and tentative, not broken.

**Marks**

| Mark | Meaning | Look |
|---|---|---|
| Violet stamp | An officer decided (reviewed, erased, attached, confirmed "different people") | Double violet ring on the entity; in drawers a small rotated stamp: *Reviewed — A. Patil, 12 Mar 2026* |
| Highlighter | Part of the open lead / the span that produced a link | Soft highlighter halo behind entities; highlighter strokes on record text |
| Identity stack | This person was assembled from several records | Two offset paper edges behind the node and a small "4 records" label |
| Cut marks | Where the Cut would fall | Short red ticks across the links to be cut |
| Crowd bundle | Too many neighbours to show | A pale node reading "+18 calls" that expands on click |

### 5.5 Layout

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Case 0231, FIR 224/2025      legal basis LB-CASE-0231          ( ) Court view │  case strip
│ 14 people, 5 companies and 9 accounts within two steps of FIR 224/2025.       │  caption
│ 3 lines are AI suggestions.                                                   │
├────────────────┬───────────────────────────────────────────────┬─────────────┤
│ Who's          │                                               │             │
│ connected?     │                                               │  Why?       │
│                │            the board (full bleed)             │  drawer     │
│ Where did the  │                                               │  (opens on  │
│ money go?      │        ink ────   dotted ····   pencil ~~     │  request,   │
│                │                                               │  pushes the │
│ Who holds it   │     [Show who else]  [Why?]  [Cut]            │  board left)│
│ together?      │      floating next to the selected item       │             │
│ When did it    │                                               │             │
│ happen?        │                                               │             │
│ Where were     │                                               │             │
│ they?          │                                               │             │
├────────────────┴───────────────────────────────────────────────┴─────────────┤
│ ▶  Jan 2025 ───▁▂▃▇▅▂▁──────●──────────── Dec 2025                  replay     │  time strip
│ Ink: on record.  Dotted: worked out from records.  Pencil: AI suggestion.     │  legend,
│ Violet stamp: decided by an officer.                                          │  always on
└──────────────────────────────────────────────────────────────────────────────┘
```

- The board is the hero and takes all remaining space.
- The question rail is text, not icons — questions are the navigation.
- The verbs float next to the selected item, not in a toolbar far away.
- The legend never hides. It teaches the language on every screen.
- Left-aligned text throughout. No centred paragraphs.

### 5.6 Screens

#### 5.6.1 Today's leads (home)

```
Today's leads
You can review about 10 a week. These 5 matter most.

1  Money moved through two new companies in six days                    High confidence
   Company X, registered 41 days before its first payment, passed ₹18L to
   Account B, which paid Person C (accused in FIR 224/2025).
   ▮▮▮▮▮▮▮ 7 on record   ▯ 1 worked out   ┈ 0 AI                     Open on board   Not worth it

2  Eight new numbers, one phone they all call                           Medium confidence
   …
```

- Ranked list (a real sequence, so numbers are allowed). Maximum 5 shown; "Show more" reveals up to 10.
- Each lead: plain title from its typology template, one sentence of why, confidence in words (High / Medium / Low), and the three-mark tally (ink / dotted / pencil counts). The tally teaches the evidence language before the board opens.
- Proactive leads outside the user's cases do not appear for the IO; for the supervisor they appear under "Waiting for your approval" (master §17.10, P-06).
- *Not worth it* asks for a reason (one of: lawful explanation found · already known · not enough on record · other) and stamps it.

#### 5.6.2 The board — five questions

Each question is a **lens**: the same nodes, re-arranged. Switching lenses animates positions (600 ms); nothing is re-fetched unless the lens needs data.

| Question on the rail | Lens | Arrangement | What fades |
|---|---|---|---|
| Who's connected? | Network | Force layout (fcose), case-scoped, two steps from the focus | Nothing |
| Where did the money go? | Money | Left→right by hop order along `TRANSFERRED_FUNDS_TO`; amounts on links; "kept 6%" under each pass-through account/company | Non-money entities fade to 15% |
| Who holds it together? | Key players | Concentric rings by disruption impact (KPP-1); the suggested cut set in the centre | Nothing; degree shown as a small number beside each person for contrast |
| When did it happen? | Time | x = first activity date; rows = entity type (people, phones, accounts, companies, places) | Undated entities go to a "no date" tray |
| Where were they? | Place | Cell towers as large translucent circles sized by footprint, placed by synthetic coordinates (no base map); phones and people sit inside the circles they share | Non-located entities fade |

Board behaviours:

- **Start small.** A case opens on the lead's entities plus two steps out. Nodes with more than 12 neighbours of one type show a crowd bundle ("+18 calls").
- **Show who else** expands one step around the selected item.
- **Selection** highlights the item and its direct links; everything else dims to 40%.
- **Hover** on any link shows a one-line tooltip in words: *"On record: bank transfer TXN-SYN-88213, ₹6,00,000, 14 May 2025."* / *"Worked out: 12 times in the same tower area at night."* / *"AI suggestion: 64% — based on shared contacts and co-presence."*
- **Court view** hides pencil and dotted lines, and hides entities connected only through them. The prosecutor's board is always in Court view.

#### 5.6.3 The *Why?* drawer (receipts)

Opens from the right for any entity, link, lead or cut result. Three sections, always in this order, each with its mark in the heading:

```
Why?  Money moved through two new companies in six days

── On record (7) ─────────────────────────────────  solid ink rule
  FIR 224/2025, paragraph 2                                       Open record
  "…received payments at the shop premises from Ali bhai…"   ← Tiro, highlighted span
  Bank transfer TXN-SYN-88213, ₹6,00,000, 14 May 2025             Open record
  Company registration SYNTH-REG-0512, registered 20 Jan 2025    Open record
  …
·· Worked out from records (1) ····················  dotted rule
  Person A and Person C are 3 steps apart through two companies.
  How: path over the 5 records above.
~~ AI suggestions (0) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  pencil rule

How sure is C.I.D.?   High — 7 of 8 items are on record; identities matched at 0.97.
How much the AI relied on this:   concern drops from 0.94 to 0.21 without these 6 links.
Model hgt-2026-03-01-a1f3. Legal basis check passed.

What this does not show
  • that any transfer was unlawful
  • that Person A knew about Person C's case
  • Lawful patterns that look like this: holding companies, payment aggregators, new businesses
```

- Record text is shown in Tiro with the extracted span highlighted (offsets from extraction).
- *Open record* opens a full record sheet over the drawer.
- *What this does not show* comes from the typology's false-positive list (master §15) — fixed text per typology, never generated.

#### 5.6.4 Identity stack

- A person assembled from several records shows the stacked-paper edge and "4 records".
- Click the stack: cards fan out from the node (not a modal). Each card shows the name *as written in the source* (Tiro, original script), source type, date, and record link.
- Between cards, chips explain the match in words: *sounds alike*, *same phone*, *same birth date*, *same address*, *similar context*. Match confidence shown once: *"Matched at 0.96, merged automatically."* or *"Matched at 0.82 — merged after review by S. Desai"* with a stamp.
- Supervisors see *Split this identity* (master §11.11). Splitting re-draws the board and records a stamp.

#### 5.6.5 Cut (disruption simulation)

1. Choose *Cut* on a person, or press *Suggest a cut* in the key-player lens (KPP-1 set, default 2 people).
2. Red cut marks appear across the links that would be cut. A small bar reads: *"Cut Person A and Person F?"* [Cut] [Cancel].
3. On Cut, the two nodes lift away and fade; the remaining network drifts into islands (packed layout, 800 ms). Each island gets a label: *"Group 1, 9 people."*
4. The result sentence: *"Splits into 3 groups. The largest keeps 38% of members. Before: everyone could reach everyone in 4 steps or fewer."*
5. Fixed caveat under every result: *"Shows structure only — not who would take over or how the group would adapt."* (master C-10)
6. *Undo cut* restores the network. Cuts are simulations: nothing in the graph changes.

#### 5.6.6 Replay (time strip)

- Bottom strip with an activity trace (links per week) and a draggable handle.
- Dragging shows the network as it stood on that date (`valid_from`/`valid_to`). Play animates from start to end in ~10 seconds.
- A small note distinguishes *"when it happened"* from *"when C.I.D. learned it"* (master §12.6); replay uses when it happened.

#### 5.6.7 Review queue (supervisor)

- Pairs side by side, each record in Tiro, differences highlighted.
- Match evidence as chips, with the score.
- Two buttons only: *Same person* / *Different people*. Both stamp. Keyboard: `S` / `D`.
- Header: *"12 pairs waiting. These are between 0.75 and 0.95 — C.I.D. will not merge them without you."*

#### 5.6.8 Case file and packet

- A case holds attached entities, leads, decisions and notes.
- *Build case packet* produces three sections — On record / Worked out / AI suggestions — plus model versions, legal basis, record hashes and the audit excerpt, as a printable page and a downloadable bundle.
- The packet cover states: *"AI suggestions are investigative leads, not evidence."*

#### 5.6.9 Audit and "How well does it work?"

- Audit page (auditor, supervisor): the chain of entries with who / what / when / under which case, and a *Verify chain* button → *"Verified — 1,284 entries, no gaps. Last seal 14:02."* Tampering with a row in the database must make verification fail and point to the first broken entry.
- Metrics page (everyone): results on the synthetic world, each with one sentence of meaning, plus a fixed note: *"Measured on synthetic data with known answers. Not a measure of real-world accuracy."*

### 5.7 Motion

Motion is used only when it shows what changed. Allowed moments:

| Moment | Duration | Easing |
|---|---|---|
| Identity collapse (first open of a lead; skippable; once per session) | 700 ms | ease-in-out |
| Lens switch (positions glide) | 600 ms | ease-in-out-cubic |
| Cut (lift away, drift into islands) | 300 + 800 ms | ease-out |
| Drawer open / close | 200 ms | ease-out |
| Stack fan-out | 250 ms | ease-out, 30 ms stagger |
| Replay | ~10 s for full range | linear |

No entrance animations on page load, no hover animations on rows, no pulsing alerts. With `prefers-reduced-motion`, all durations become 0 and the identity collapse shows the final state with a "4 records" note.

### 5.8 Words

| Say | Never say |
|---|---|
| Lead | Suspect list, target |
| On record / worked out / AI suggestion | Evidence (for anything but source records), proven, confirmed |
| How sure C.I.D. is | Guilt score, threat level |
| Key player, holds the network together | Kingpin (only the typology name in the drawer), mastermind |
| In the same tower area | Met, was at (for cell-tower data) |
| Not worth it | Dismiss, reject |
| Erase suggestion | Delete |
| Build case packet | Export, generate report |

Copy rules: sentence case, active verbs, buttons say exactly what happens (*Build case packet* → toast *"Case packet built"*). Errors say what happened and what to do: *"Pick a case first. C.I.D. only answers questions inside an authorised case."* Empty board: *"Start from a lead or search for a name, phone or account."*

### 5.9 Accessibility

- Evidence class is carried by line style **and** words (legend, tooltips, drawer headings), never colour alone.
- WCAG AA contrast for text on Desk and Sheet.
- Full keyboard: `Tab` through leads; on the board `←/→` cycle neighbours, `E` show who else, `W` why, `X` cut, `C` court view, `Space` play replay, `Esc` close drawer.
- Visible focus ring (2 px Blue ink, 2 px offset).
- Screen-reader text for each selected entity: type, name, number of links by class.

---

## 6. Functional requirements

| ID | Requirement | Master | Acceptance |
|---|---|---|---|
| PR-01 | Generate a seeded synthetic world with ground truth (§7) | D-18 | Same seed ⇒ byte-identical output; ground-truth file lists injected networks and true identities |
| PR-02 | Ingest all sources with provenance (source system, ingested_at, legal basis) and store each source record retrievable by `source_record_id` | D-04 | 100% of records retrievable; ingest rejects rows without legal basis |
| PR-03 | Normalise names, phones, dates (UTC + source tz), offence codes (IPC and BNS) | §10.2, D-17 | Unit tests on formats and a mixed IPC/BNS sample |
| PR-04 | Extract entities and relations from FIR narratives with character offsets | D-07, D-08 | Entity F1 and relation F1 reported against ground truth |
| PR-05 | Resolve identities with Indic phonetic keys, blocking, Fellegi-Sunter and context similarity; three tiers | D-05, D-06 | Mohammad Ali variants merge; the two Raj Kumars do not; ER precision and recall reported |
| PR-06 | Review queue for the 0.75–0.95 band; decisions stamped and reversible | D-06, §11.11 | Accept/reject changes the graph; split restores prior entities |
| PR-07 | Build the graph with mandatory edge properties and `evidence_class` | D-04, P-01 | A test asserts every DOCUMENTED edge has a resolvable `source_record_id` |
| PR-08 | Case-scoped graph queries; queries without case ID and legal basis are rejected and logged | D-15, G-01 | API returns 403 with the plain message; audit shows the refusal |
| PR-09 | Centrality, communities and KPP-1 per case network | D-09 | Known insulated principal ranks in top 2 by KPP-1 but not top 5 by degree |
| PR-10 | Cut simulation returns components, largest-group share, reachability before/after, sentence | F-04 | Deterministic for the same input |
| PR-11 | Co-presence detection producing DERIVED `CO_LOCATED_WITH` edges | D-20, D-21 | The injected 2 a.m. ring is found; co-workers look-alike is flagged as lower frequency or excluded |
| PR-12 | HGT anomaly scoring on the heterogeneous graph | D-11 | Precision@10 and AUC-PR reported on held-out synthetic labels |
| PR-13 | Link prediction producing INFERRED suggestions (pencil) | F-03 | Hits@10 and MRR reported; suggestions never stored as documented |
| PR-14 | Explanation per GNN alert with fidelity | D-12 | Every GNN alert has an evidence subgraph and before/after probability |
| PR-15 | Typology detection for T-01, T-02/T-03, T-04, T-05, T-08 | §15 | Each injected network produces its typology lead |
| PR-16 | Risk fusion and ranked leads with confidence in words | D-23 | Leads page shows ≤5 by default, each with evidence tally |
| PR-17 | Pin a record / Erase for pencil lines, enforcing no automatic promotion | §19.4 | Pin with a record that does not state the link is refused |
| PR-18 | Court view and prosecutor lock | F-02 | Prosecutor API responses contain no INFERRED or DERIVED edges |
| PR-19 | Case packet with three sections, hashes and audit excerpt | F-12 | Packet hash manifest verifies |
| PR-20 | Tamper-evident audit chain with verify | G-05, G-15 (P-09) | Editing any audit row makes verify fail at that row |
| PR-21 | Metrics page from the latest pipeline run | §26 | Every number traceable to a run ID and seed |
| PR-22 | The Case Board experience in §5 | §21 | Demo story (§4) runs start to finish |

---

## 7. The synthetic world

A fictional district ("Demo District") with fictional towns, towers and coordinates. **No real people, places, companies or numbers.** Names come from Faker `en_IN` and `hi_IN` plus curated name lists.

| Source | Approx. size | Notes |
|---|---|---|
| People (true identities) | 1,500 | ~20% appear under 2–5 name variants across sources, in Latin and Devanagari (plus a few Tamil and Bengali forms) |
| FIRs | 500 | Narratives in English, Romanised Hindi (code-mixed) and some Devanagari names; ~60% BNS sections, ~40% older IPC sections |
| CDR rows | 5,000 | calling, called, timestamp, duration, cell_tower |
| Transactions | 2,000 | from/to account, amount, timestamp, channel, txn_id |
| Accounts (KYC) | 2,000 | holder, open date, KYC status |
| Phone registrations | 1,800 | subscriber, activation date, IMSI |
| Companies | 150 | registration no., incorporation date, registered address, directors |
| Vehicles | 300 | registration, owner |
| Cell towers | 60 | synthetic lat/lon, footprint radius (300 m urban – 3 km rural) |

**Injected networks (ground truth)**

| ID | Network | Typology | Built so that… |
|---|---|---|---|
| N1 | Shell chain around Person A | T-01, T-08 | Person A has only 3 direct links but high KPP-1; two companies share a director and address, incorporated weeks before first payment; each hop keeps <10% |
| N2 | Mule fan-out | T-02, T-03 | A hub account splits funds to 12 recently opened accounts below a **synthetic** threshold (₹50,000, labelled synthetic — real thresholds are master Q-DAT-10) |
| N3 | Burner tree + night ring | T-04, T-05 | 8 batch-activated short-lived numbers call one persistent number; 4 people share a tower area at ~2 a.m. 10+ times with zero calls between them |

**Training and test networks.** Besides N1–N3 (the demo networks), the generator injects ~30 more networks of the same three kinds across the district, with different sizes and timings. Models are trained and tested on *different* networks (split by network, never by node), so the demo networks are never seen in training.

**Look-alikes (to show honesty about false positives):** a payroll fan-out, a family sharing one phone, co-workers co-present daytime, a legitimate holding company.

**Identity traps:** Mohammad Ali across four sources and scripts (must merge); two different Raj Kumars (must not merge); Chatterjee/Chaterjee/Chattopadhyay (formal-name equivalence); Azhagiri/Alagiri.

**Demo case:** Case 0231 assigned to `io.patil`, anchored on FIR 224/2025, which names Person C.

---

## 8. Non-functional requirements

| Area | Requirement |
|---|---|
| Runs on | One Linux laptop with an NVIDIA GPU (team machine: Pop!_OS 24.04), Docker, Python 3.12, Node 20+ |
| No external calls at runtime | After models and fonts are downloaded once, the full system runs with networking off. A test proves it. |
| Determinism | One seed controls world generation, splits and training. Re-running the pipeline with the same seed gives the same leads. |
| Speed (prototype targets) | Board interactions feel instant (<100 ms); case graph and ego queries p95 < 1 s; full pipeline run < 20 min on the dev machine |
| Board size | ≤ 300 nodes visible at once; crowds bundled |
| Traceability | Every lead, suggestion and metric carries model version and pipeline run ID |
| Privacy by design | Phone and account identifiers are keyed-hashed in the graph; raw values live only in the source-record store (P-08) |
| Audit | Every API request, allowed or refused, is written to the audit chain |
| Accessibility | §5.9 |

---

## 9. Out of scope for this prototype

Everything in §2 non-goals, plus: travel records and trafficking corridors (T-06); emerging-network detection (T-07) except as `STRETCH`; TGN / EvolveGCN / CARE-GNN / PC-GNN (Advanced tier); PGExplainer and SubgraphX; night-mode theme (`STRETCH`); multi-case cross-network analysis beyond the analyst's assigned cases.

---

## 10. Prototype decisions to confirm

These answer open questions in the master **for the prototype only**. Confirm them (or change them) and record them in master §31 as D-26 onwards before building.

| ID | Open item (master) | Prototype default | Why |
|---|---|---|---|
| P-01 | Evidence fields (§09.5), rules (§19.4) | Adopt as written: `evidence_class`, `extraction_confidence`, `resolution_confidence`, `inference_confidence`, `derived_from`, `method`, `model_version`, `record_hash` | Lead-vs-evidence cannot be built without them |
| P-02 | Ontology gaps (§09.9, C-03, C-13, C-14) | Add `DIRECTOR_OF`, `VICTIM_IN`, `WITNESS_IN`, `REGISTERED_AT`; allow `PhoneNumber` as a `PRESENT_AT` source; allow `Organization` as an `OWNS` source for accounts | Typologies T-01, T-05 and the demo need them |
| P-03 | Inferred edges in graph vs overlay (Q-ARC-05) | Store AI suggestions as a separate relationship type `AI_SUGGESTED` (with `suggested_type`) | A query can never mix them in by accident |
| P-04 | `CALLED` per call vs aggregated (Q-ARC-03) | Per call in the graph; the API aggregates for display | Keeps one source record per edge |
| P-05 | What "a network" is (Q-ARC-04) | Case-scoped: two steps from the case's entities; Leiden communities for grouping leads | Matches purpose limitation |
| P-06 | Proactive leads scope (C-05) | Leads outside an assigned case wait for supervisor approval | Master §17.10 proposal |
| P-07 | Risk fusion and confidence (Q-AIM-11) | Equal-weight mean of available component scores (labelled "uncalibrated"); confidence High if ≥70% of the evidence subgraph is on record and all identities ≥0.95, Medium if ≥40%, else Low | Simple, explainable, honest |
| P-08 | Identifier hashing (C-22) | Normalise then HMAC-SHA256 with a local key; raw values only in the source-record store | Fixes enumeration risk |
| P-09 | Hash-chained ledger (Q-ARC-07, C-16) | Adopt for the audit log: each entry hashes the previous; a seal (Merkle root) every 100 entries | Tamper-evidence; answers the Blockchain & Cybersecurity theme |
| P-10 | Deployment wording (C-04) | Say "runs entirely on the local machine; no external network calls at runtime" — a claim we can prove | Avoids "100% offline" contradictions |
| P-11 | Name (Q-PRD-01) | C.I.D. | Deck and master |
| P-12 | Natural-language assistance (Q-PRD-03) | Not in the prototype | Hallucination risk; scope |
| P-13 | Class of merged identities (Q-AIM-05) | Merges are DERIVED (probabilistic linkage) with `resolution_confidence`; review-band merges exist only after a stamp | Keeps AI marks off identities |
| P-14 | Co-presence parameters (Q-AIM-10) | Same tower within ±15 min; DBSCAN over (tower, hour-of-day); ≥4 events | Finds N3, rejects one-off coincidences |
| P-15 | KPP algorithm (Q-AIM-07) | Greedy KPP-1 on distance-weighted fragmentation, k = 2 default (1–4 allowed) | Small graphs; clear result |
| P-16 | Typology mechanism (Q-AIM-04) | Hybrid: graph queries name the pattern; HGT score adds anomaly strength | Deterministic names, learned ranking |
| P-17 | Where source records live (Q-ARC-01) | PostgreSQL table `source_records`, keyed by `source_record_id`, with `record_hash` | F-01 needs click-through to the original |
| P-18 | Source record as node or property (Q-ARC-02) | Property (`source_record_id` on edges); no `SourceRecord` nodes | Keeps the graph small and the master schema intact |

---

## 11. Success criteria

**Demo:** the story in §4 runs start to finish on a fresh machine, twice in a row, with networking off.

**Metrics on the synthetic world** (report, don't promise): entity F1, relation F1, ER precision / recall / false-merge count, precision@10 and AUC-PR for anomaly leads, Hits@10 and MRR for suggestions, mean explanation fidelity, ego-query p95. The master's targets (entity F1 0.85+, relation F1 0.75+, ER precision > 0.98, fidelity > 0.7) are the bar; if the prototype misses one, the metrics page says so.

---

## 12. What the prototype must never say

- "Proof", "confirmed", "guilty", or "evidence" for anything the AI produced.
- A percentage presented as the chance someone committed a crime.
- "GPS", "met at" or any building-level location from cell-tower data.
- Who would "take over" after a cut.
- "100% offline" or "tamper-proof" (say "no external calls at runtime" and "tamper-evident").
- Any metric from the synthetic world presented as real-world accuracy.
