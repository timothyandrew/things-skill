---
name: things
description: Manage a local Things 3 task manager (macOS) — create, read, search, edit, complete, and organize to-dos and projects. Use whenever the user wants to capture a task or query their tasks, e.g. "add this to Things", "add a TODO to Things", "remind me to…", "what's on my Things Today list", "search my Things database", "mark that done in Things", "create a project in Things", or any mention of their Things to-dos, projects, areas, or tags.
---

# Things 3

Two-channel interface to the local Things 3 app:
- **Write** (create/edit/complete) → `scripts/things_write.py`, the official `things:///` URL scheme.
- **Read** (list/search/detail) → `scripts/things_read.js`, the official JXA scripting API.

Requires the Things 3 macOS app installed and running. Both scripts are in `scripts/`; run
them with absolute or skill-relative paths.

## Quick start

Capture a to-do:
```bash
scripts/things_write.py add "title=Email the contractor" when=today tags=Errand
```

See what's on Today / search:
```bash
osascript -l JavaScript scripts/things_read.js show Today
osascript -l JavaScript scripts/things_read.js search "contractor"
```

Complete it (needs auth-token — see below):
```bash
scripts/things_write.py complete id=<id-from-a-read>
```

## Choosing the channel

| User wants to… | Use |
|---|---|
| Add a to-do / project, jot something down | `things_write.py add` / `add-project` |
| List, search, or inspect existing items | `things_read.js show/search/todo` |
| Edit, move, retag, set date, complete, cancel | `things_write.py update` / `complete` / `cancel` |
| Do several creates/edits at once | `things_write.py json` (one user-visible action) |
| Just open a view in the app | `things_write.py show` / `search` |

## Workflow notes

- **Editing requires an id, and ids come from reads.** To complete/edit "that task", first
  `things_read.js search <text>`, pick the matching `id`, then `complete`/`update id=<id>`.
  Don't guess ids. If a search is ambiguous, show the candidates and ask which one.
- **Tags must already exist** in Things; unknown tag names are silently dropped. Check with
  `things_read.js tags` if unsure.
- **Targets** for `list=`/`area=` come from `things_read.js lists`. Use exact names.
- **Default `when`.** Don't auto-schedule. Only set `when=today` (or another date) when the
  user implies timing ("today", "tomorrow", "next week"). Otherwise leave it in the Inbox.
- **Confirm destructive edits.** Bulk completes/cancels or anything touching many items:
  list what will change and confirm first. Single straightforward adds need no confirmation.
- Both scripts print what they did (the write script echoes the fired URL with the token
  redacted). Report the outcome plainly; if a read can't find the item, say so.

## Auth token (one-time, for editing)

`update`, `update-project`, `complete`, `cancel`, and json-updates need an auth token.
The write script reads it from `THINGS_AUTH_TOKEN`, else `~/.config/things/auth-token`.
If neither is set it prints setup instructions and exits. To set up:
Things → Settings → General → Enable Things URLs → Manage → copy token, then e.g.
`mkdir -p ~/.config/things && pbpaste > ~/.config/things/auth-token`.
Creating and reading items needs **no** token.

## References

- **`references/url-scheme.md`** — every write command and parameter (add, add-project,
  update, json, show, search) with formats and limits. Read before constructing non-trivial
  writes (json payloads, headings, checklists, date-times, clearing fields).
- **`references/reading.md`** — read commands, the to-do object shape, gotchas (no-date
  sentinel, `--all` cost), and how to write ad-hoc JXA `.whose()` queries.
