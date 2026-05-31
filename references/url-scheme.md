# Things URL Scheme Reference (write path)

`scripts/things_write.py` builds and fires these `things:///` URLs for you, percent-encoding
every value. This file documents every command and parameter so you know which `key=value`
pairs are valid. Source: https://culturedcode.com/things/support/articles/2803573/

## Contents
- [add](#add) — new to-do
- [add-project](#add-project) — new project
- [update](#update) — edit a to-do (needs auth-token)
- [update-project](#update-project) — edit a project (needs auth-token)
- [json](#json) — batch create/update
- [show](#show) / [search](#search) — open the UI
- [Value formats](#value-formats)

## add
Create a to-do. `things_write.py add key=value ...`

| Param | Notes |
|---|---|
| `title` | To-do name (≤4000 chars). Ignored if `titles` given. |
| `titles` | Multiple to-dos, one per newline (`%0a`). Overrides `title`. |
| `notes` | ≤10000 chars. |
| `when` | `today`, `tomorrow`, `evening`, `anytime`, `someday`, a `yyyy-mm-dd` date, a date-time `yyyy-mm-dd@HH:MM`, or natural language (`in 3 days`, `next tuesday`). |
| `deadline` | Due date `yyyy-mm-dd`. |
| `tags` | Comma-separated **existing** tag names (unknown tags are ignored). |
| `checklist-items` | One per newline, ≤100. |
| `list` / `list-id` | Target project or area (by name / id). `list-id` wins. |
| `heading` / `heading-id` | Section within a project. |
| `completed` / `canceled` | `true`/`false`. `canceled` wins. |
| `show-quick-entry` | Show the entry dialog instead of adding. |
| `reveal` | Navigate to the new to-do. |
| `creation-date` / `completion-date` | ISO8601 timestamps. |

## add-project
Create a project. `things_write.py add-project key=value ...`

| Param | Notes |
|---|---|
| `title`, `notes`, `when`, `deadline`, `tags` | As above. |
| `area` / `area-id` | Containing area. |
| `to-dos` | Initial to-do titles, one per newline. |
| `completed` / `canceled`, `reveal`, `creation-date`, `completion-date` | As above. |

## update
Edit an existing to-do. **Requires `id`** and an **auth-token** (auto-injected).
`things_write.py update id=<id> key=value ...`

Replace vs. append:
- `title`, `notes`, `tags`, `checklist-items` — **replace** the field.
- `prepend-notes`, `append-notes`, `add-tags`, `prepend-checklist-items`, `append-checklist-items` — additive.
- `when`, `deadline`, `list`/`list-id`, `heading`/`heading-id`, `completed`, `canceled`, `reveal`, `duplicate`, `creation-date`, `completion-date` — as in `add`.

Notes:
- Passing a key with an **empty value** (`notes=`) clears that field.
- Cannot modify repeating to-dos (`when`, `deadline`, `completion-date`, `duplicate`).
- Convenience: `things_write.py complete id=<id>` and `cancel id=<id>` map to `update ... completed/canceled=true`.

## update-project
Edit an existing project. **Requires `id`** + auth-token. Same params as `update`,
plus `area`/`area-id` instead of `list`. `completed`/`canceled` are ignored unless all
child items are already completed.

## json
Batch create/update with one payload. `things_write.py json 'data=<json>'`
(auth-token auto-injected when the payload contains an update operation).

`data` is a JSON **array** of objects:
```json
[
  {"type":"to-do","attributes":{"title":"A","when":"today","checklist-items":[{"type":"checklist-item","attributes":{"title":"x"}}]}},
  {"type":"project","attributes":{"title":"P","items":[
     {"type":"heading","attributes":{"title":"Phase 1"}},
     {"type":"to-do","attributes":{"title":"B"}}
  ]}},
  {"type":"to-do","operation":"update","id":"<id>","attributes":{"completed":true}}
]
```
Object types: `to-do`, `project`, `heading`, `checklist-item`. `operation` is `create`
(default) or `update` (needs `id`). Use this for anything multi-item or mixed create+update —
it is one user-visible action instead of many.

## show
Open something in the Things UI (no data returned). `things_write.py show id=<id>` or
`show query=<name>`.
- `id`: a built-in list (`inbox`, `today`, `anytime`, `upcoming`, `someday`, `logbook`,
  `tomorrow`, `deadlines`, `repeating`, `all-projects`, `logged-projects`) or an item/area/
  project/tag id. `id` wins over `query`.
- `filter`: comma-separated tag names to filter the shown list.

## search
Open Things' search. `things_write.py search query=<text>` (query optional).
This only opens the UI — to actually *read* results, use `scripts/things_read.js search`.

## Value formats
- Dates: `yyyy-mm-dd`; date-time: `yyyy-mm-dd@HH:MM`; ISO8601 for `*-date` params.
- Booleans: `true` / `false`.
- Multi-line fields (`titles`, `checklist-items`, `to-dos`): put real newlines in the value;
  `things_write.py` encodes them. The shell `$'...\n...'` form is handy.
- Limits: 250 added items / 10s.
