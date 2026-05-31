# Reading Things data (JXA scripting API)

The `things:///` URL scheme is **write-only** — its `show`/`search` commands open the UI but
return nothing. To read or search, `scripts/things_read.js` queries Things 3's official
scripting interface via JXA (`osascript -l JavaScript`) and prints JSON.

Run it with: `osascript -l JavaScript scripts/things_read.js <command> [args]`

## Commands
| Command | Output |
|---|---|
| `lists` | `{builtin:[...], areas:[...], projects:[...]}` — every valid `list=` / `show` target. |
| `show <name> [--all]` | To-dos in a built-in list, project, **or** area. Open only unless `--all`. |
| `search <text> [--all]` | To-dos whose name **or** notes contain `<text>`. Open only unless `--all`. |
| `todo <id>` | Full detail incl. notes, checklist, creation/completion dates. |
| `projects` | `[{id,name,area}]` |
| `areas` | `[{id,name}]` |
| `tags` | tag names |

To-do objects carry: `id`, `name`, `status` (`open`/`completed`/`canceled`), `when`
(activation/start date), `deadline` (due date), `tags` (comma string), `project`, `area`.

## Notes & gotchas
- **IDs feed writes.** The `id` from any read command is exactly what `update`/`complete`/
  `cancel`/`show id=` expect. Typical flow: `search` → take an `id` → `complete id=<id>`.
- **`--all` is slow** — it scans the Logbook (all completed history). Default to open items.
- **No-date sentinel.** Things stores "no date" as year ≥ 4000; the script normalizes these
  to `null`, so a `null` `when`/`deadline` genuinely means unset.
- **Built-in lists** are `Inbox, Today, Anytime, Upcoming, Someday, Logbook, Trash`. Note
  `Upcoming` is scheduled future items; `Anytime` excludes them.
- Read-only by design — it never mutates. All mutations go through `things_write.py`.

## Ad-hoc queries
For anything the subcommands don't cover, write a one-off JXA snippet — the API exposes
`toDos`, `projects`, `areas`, `tags`, `lists`, each with `.whose({...})` filters. Example:
```bash
osascript -l JavaScript -e '
const t = Application("Things3");
JSON.stringify(t.lists.byName("Today").toDos().whose({status:"open"})().map(x=>x.name()));'
```
`.whose()` operators: `_contains`, `_beginsWith`, `_endsWith`, `_equals`, `_and`, `_or`, `_not`.
