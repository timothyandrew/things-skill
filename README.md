# things-skill

A [Claude Code](https://claude.com/claude-code) **skill** for managing a local
[Things 3](https://culturedcode.com/things/) task manager on macOS — create, read, search,
edit, complete, and organize to-dos and projects from natural language.

Once installed, ask Claude things like:

- "add *buy milk* to Things for today"
- "what's on my Things Today list?"
- "search my Things database for the contractor task and mark it done"
- "create a project in Things called *Kitchen reno* with three to-dos"

## How it works

Two channels to the local app, both using Things' **official** interfaces:

| Channel | Mechanism | Used for |
|---|---|---|
| **Write** — `scripts/things_write.py` | the `things:///` [URL scheme](https://culturedcode.com/things/support/articles/2803573/) | add, update, complete/cancel, batch json, show/search |
| **Read** — `scripts/things_read.js` | JXA scripting API (`osascript -l JavaScript`) | list, search, and inspect items (the URL scheme can't return data) |

`SKILL.md` is the entry point Claude loads; `references/` holds the full URL-scheme and
read-API documentation, loaded on demand.

## Requirements

- macOS with the **Things 3** app installed and running.
- **Editing** existing items (`update`, `complete`, `cancel`) needs a Things auth token —
  enable it in **Things → Settings → General → Enable Things URLs → Manage**, then store it:

  ```bash
  mkdir -p ~/.config/things && pbpaste > ~/.config/things/auth-token
  ```

  (or set `THINGS_AUTH_TOKEN`). Creating and reading items needs **no** token.

## Install

Clone into your Claude Code skills directory:

```bash
git clone https://github.com/timothyandrew/things-skill.git ~/.claude/skills/things
```

Claude will discover it automatically and invoke it when a request matches.

## Usage (direct)

The scripts also work standalone:

```bash
# add
scripts/things_write.py add "title=Email the contractor" when=today tags=Errand

# read
osascript -l JavaScript scripts/things_read.js show Today
osascript -l JavaScript scripts/things_read.js search "contractor"

# complete (needs auth token)
scripts/things_write.py complete id=<id-from-a-read>
```

See `references/url-scheme.md` and `references/reading.md` for the complete command and
parameter reference.

## License

MIT
