#!/usr/bin/env osascript -l JavaScript
//
// Read-only access to the local Things 3 database via JXA (official scripting API).
//
// Usage:
//   osascript -l JavaScript things_read.js <command> [args...]
//
// Commands:
//   lists                    Built-in list names + area names + project names (valid targets for `list=`)
//   show   <name>            To-dos in a built-in list, project, OR area (open items only)
//   show   <name> --all      ...including completed/canceled items
//   search <text>            Open to-dos whose name OR notes contain <text>
//   search <text> --all      ...search completed/canceled items too (slow; scans Logbook)
//   todo   <id>              Full detail for one to-do (id from any other command)
//   projects                 All project names + ids
//   areas                    All area names + ids
//   tags                     All tag names
//
// Output is always JSON on stdout. Dates are ISO strings or null.

function run(argv) {
  const things = Application('Things3');
  const cmd = (argv[0] || '').toLowerCase();
  const rest = argv.slice(1);
  const includeAll = rest.includes('--all');
  const args = rest.filter(a => a !== '--all');

  // Things stores "no date" as a sentinel far in the future (year >= 4000).
  function cleanDate(d) {
    if (!d) return null;
    try { if (d.getFullYear() >= 4000) return null; } catch (e) { return null; }
    return d.toISOString();
  }

  function brief(t) {
    let project = null, area = null;
    try { if (t.project()) project = t.project().name(); } catch (e) {}
    try { if (t.area()) area = t.area().name(); } catch (e) {}
    return {
      id: t.id(),
      name: t.name(),
      status: t.status(),                 // open | completed | canceled
      when: cleanDate(t.activationDate()), // the "when"/start date
      deadline: cleanDate(t.dueDate()),
      tags: t.tagNames(),                  // comma-separated string
      project: project,
      area: area,
    };
  }

  function full(t) {
    const b = brief(t);
    b.notes = t.notes();
    b.creationDate = cleanDate(t.creationDate());
    b.completionDate = cleanDate(t.completionDate());
    try { b.checklist = t.checklistItems().map(c => ({ name: c.name(), status: c.status() })); }
    catch (e) { b.checklist = []; }
    return b;
  }

  function filterStatus(arr) {
    return includeAll ? arr : arr.filter(t => t.status() === 'open');
  }

  let out;
  switch (cmd) {
    case 'lists': {
      out = {
        builtin: ['Inbox', 'Today', 'Anytime', 'Upcoming', 'Someday', 'Logbook', 'Trash'],
        areas: things.areas.name(),
        projects: things.projects.name(),
      };
      break;
    }
    case 'show': {
      const name = args[0];
      if (!name) throw new Error('show requires a list/project/area name');
      let todos = null;
      // Try built-in list, then project, then area.
      try { todos = things.lists.byName(name).toDos(); } catch (e) {}
      if (todos === null) { try { todos = things.projects.byName(name).toDos(); } catch (e) {} }
      if (todos === null) { try { todos = things.areas.byName(name).toDos(); } catch (e) {} }
      if (todos === null) throw new Error('No list, project, or area named: ' + name);
      out = filterStatus(todos).map(brief);
      break;
    }
    case 'search': {
      const text = args[0];
      if (!text) throw new Error('search requires text');
      const q = { _or: [{ name: { _contains: text } }, { notes: { _contains: text } }] };
      let matches = things.toDos.whose(q)();
      matches = filterStatus(matches);
      out = matches.map(brief);
      break;
    }
    case 'todo': {
      const id = args[0];
      if (!id) throw new Error('todo requires an id');
      out = full(things.toDos.byId(id));
      break;
    }
    case 'projects':
      out = things.projects().map(p => ({ id: p.id(), name: p.name(), area: (p.area() ? p.area().name() : null) }));
      break;
    case 'areas':
      out = things.areas().map(a => ({ id: a.id(), name: a.name() }));
      break;
    case 'tags':
      out = things.tags.name();
      break;
    default:
      throw new Error('Unknown command: ' + cmd + '. See header for usage.');
  }
  return JSON.stringify(out, null, 2);
}
