#!/usr/bin/env python3
"""
Write to Things 3 via the official things:/// URL scheme.

Usage:
    things_write.py <command> key=value [key=value ...]

Commands:
    add            Create a to-do        (params: title, notes, when, deadline, tags,
                                          checklist-items, list, heading, ...)
    add-project    Create a project      (params: title, notes, when, deadline, tags,
                                          area, to-dos, ...)
    update         Edit a to-do          (REQUIRES id=...; needs auth-token)
    update-project Edit a project        (REQUIRES id=...; needs auth-token)
    complete       Mark a to-do done     (REQUIRES id=...; sugar for: update id=.. completed=true)
    cancel         Cancel a to-do        (REQUIRES id=...; sugar for: update id=.. canceled=true)
    json           Batch create/update   (params: data=<json string>; needs auth-token for updates)
    show           Open a list/item in the UI (params: id=... OR query=...)
    search         Open search in the UI (params: query=...)

Multi-value fields: put real newlines in the value (the shell handles quoting), e.g.
    things_write.py add "title=Buy milk" $'checklist-items=2%\nWhole\nOat'   # or literal newlines

Auth token (for update / update-project / json-updates): read from, in order,
    1. env var  THINGS_AUTH_TOKEN
    2. file     ~/.config/things/auth-token   (first line, trimmed)
Get the token in Things: Settings -> General -> Enable Things URLs -> Manage.

By default write commands open Things in the background (-g). `show`/`search` come to the
foreground so you can see the result. Pass --reveal to force foreground on any command.
"""
import os
import sys
import subprocess
from pathlib import Path
from urllib.parse import quote

WRITE_CMDS = {"add", "add-project", "update", "update-project", "complete", "cancel", "json"}
UI_CMDS = {"show", "search"}
NEEDS_TOKEN = {"update", "update-project", "complete", "cancel"}  # json: only if it contains updates


def load_token():
    tok = os.environ.get("THINGS_AUTH_TOKEN", "").strip()
    if tok:
        return tok
    f = Path.home() / ".config" / "things" / "auth-token"
    if f.exists():
        return f.read_text().splitlines()[0].strip()
    return None


def die(msg):
    sys.stderr.write(msg.rstrip() + "\n")
    sys.exit(1)


def main(argv):
    if not argv:
        die(__doc__)
    cmd = argv[0]
    reveal = "--reveal" in argv[1:]
    pairs = [a for a in argv[1:] if a != "--reveal"]

    if cmd not in WRITE_CMDS and cmd not in UI_CMDS:
        die(f"Unknown command: {cmd}\n{__doc__}")

    # Parse key=value params.
    params = {}
    for p in pairs:
        if "=" not in p:
            die(f"Bad param (need key=value): {p!r}")
        k, v = p.split("=", 1)
        params[k] = v

    # Desugar complete/cancel into update.
    url_cmd = cmd
    if cmd in ("complete", "cancel"):
        if "id" not in params:
            die(f"{cmd} requires id=... (get it from things_read.js)")
        url_cmd = "update"
        params["completed" if cmd == "complete" else "canceled"] = "true"

    # Inject auth-token where required.
    needs_token = cmd in NEEDS_TOKEN or (cmd == "json" and '"operation":"update"' in params.get("data", "").replace(" ", ""))
    if needs_token:
        token = load_token()
        if not token:
            die("No auth-token found. Set THINGS_AUTH_TOKEN or write ~/.config/things/auth-token\n"
                "Get it in Things: Settings -> General -> Enable Things URLs -> Manage.")
        params["auth-token"] = token

    if url_cmd in ("update", "update-project") and "id" not in params:
        die(f"{url_cmd} requires id=... (get it from things_read.js)")

    # Build the URL with each value percent-encoded.
    query = "&".join(f"{quote(k, safe='')}={quote(v, safe='')}" for k, v in params.items())
    url = f"things:///{url_cmd}?{query}" if query else f"things:///{url_cmd}"

    # Redacted echo for transparency.
    redacted = url
    if "auth-token" in params:
        redacted = url.replace(quote(params["auth-token"], safe=""), "***")
    print(redacted)

    foreground = reveal or cmd in UI_CMDS
    open_cmd = ["open", url] if foreground else ["open", "-g", url]
    subprocess.run(open_cmd, check=True)


if __name__ == "__main__":
    main(sys.argv[1:])
