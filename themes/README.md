# Themes for the folders page

`ccstay folders` writes one HTML file. The page core owns the data, the language (English or Traditional Chinese from the phone's setting), the state filters, the theme switch, the page age, the copy toast and what is remembered between visits. A theme only draws. Every theme in this folder is embedded in the page, the viewer switches between them at the top, and Bento is the default. `ccstay themes` lists them; `ccstay folders --theme <name>` starts with another one.

Personal themes live in `$XDG_CONFIG_HOME/ccstay/themes/<name>/` (usually `~/.config/ccstay/themes/`) and work the same way; one with the same name as a shipped theme replaces it.

## Files

```
themes/<name>/
  theme.json   {"name": {"en": "Bento", "zh": "便當"}, "author": "you", "description": {"en": "...", "zh": "..."}}
  theme.css    the look; loaded only while this theme is showing, so no scoping needed
  theme.js     ccstayTheme({ render: function (c) { ...; return html; }, mount: function (root, c) { optional } })
```

`<name>` is lowercase letters, digits and dashes. `theme.js` must not contain `</script` or `<!--`. The only outside resource allowed is Google Fonts, through `@import` at the top of `theme.css`; nothing else may be fetched. A theme that fails validation is left out with a message naming it; a theme whose `render` throws in the browser is dropped for that visit and the page shows the default instead.

## The contract

`render(c)` returns the HTML for the whole page body as one string. `c` has:

| Field | What it is |
|---|---|
| `c.data.folders[]` | `{head, name, label, path, sessions[]}`, newest folder first. `label` is `name` with `~` translated. |
| `c.data.folders[].sessions[]` | `{key, title, sub, state, when, url, hash}`, attention first. `state` is `waiting`, `working`, `idle` or `asleep`; `sub` is the worktree name or empty; `url` is empty for asleep sessions. |
| `c.data.closed[]` | `{key, cmd, title, prompt, cwd, when}`, newest first. `cmd` is the reopen command to copy. |
| `c.t` | Every string already in the viewer's language: `title`, `needsYou`, `closed`, `closedHint`, `copy`, `emptyFilter`, `state[state]`, `copyLabel(title)`, and more; read the `S` tables in `ccstay.py`. |
| `c.lang`, `c.counts`, `c.esc(s)` | `"en"` or `"zh"`; counts per state plus `all` and `closed`; HTML escaping. Escape every title, path and URL you print. |
| `c.summary`, `c.generated` | HTML for the first two lines under the heading. Put both in; the core keeps the age fresh. |
| `c.chips`, `c.switcher` | HTML for the state filters and the theme switch. Put both in; the core wires them. Style `.chips button[data-f][aria-pressed]` and leave `.skins` alone. |
| `c.empty` | The "no sessions" message when there is nothing running, otherwise empty. Show it when set. |
| `c.assign(n)` | Returns `pick(session)`, a stable number in `0..n-1` from the session id, different for every session in a folder when possible. Use it to choose a character or colour. |

What your HTML must contain, so the core can run it:

- Every session element carries `data-st="<state>"`; a session with `url` is `<a href="…" target="_blank" rel="noopener">`, otherwise not a link.
- Every folder container carries `data-grp`; the closed section carries `data-closed`; an element with `data-empty` holds `c.t.emptyFilter` and starts `hidden`.
- Each closed session is `<button type="button" data-copy="…cmd…">`. The core copies and shows the toast.
- Your CSS sets `--bg`, `--fg` and `--mute` on `:root` for light and dark; the core uses them for the switch, the toast, focus rings and selection. Dark mode is `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {…} }` plus `:root[data-theme="dark"] {…}`, because the host page may force either.
- Set `font-family` on `body`; the core already sets the margins, the safe-area gutter and `[hidden]`.

The core hides and shows elements with the `hidden` attribute, so do not force `display` on them. `mount(root, c)` runs after your HTML is in the page, for your own listeners; elements are replaced on every render, so nothing needs cleaning up.

## Preview

```sh
python3 ccstay.py folders -o /tmp/sessions.html --theme <name>
open /tmp/sessions.html
```

The page reads the browser language, so switch your browser to Chinese or English to see both. `python3 -m unittest tests.test_ccstay.Themes` runs the file checks.

## A pull request must include

- Light and dark, both looking finished
- Traditional Chinese and English, using `c.t` for every word
- Reduced motion respected: decorative animation off under `prefers-reduced-motion: reduce`, the state still readable
- 390 px wide with no horizontal scroll and the safe-area gutter kept
- No external resources except Google Fonts, no network calls, no code loaded or built at runtime. The page shows session titles and folders, so `ccstay themes` refuses a theme with any of these, and every theme is read by a person before it is merged
- Your own original art, or art under a licence that allows it, named in `theme.json`
- Screenshots of both colour schemes in the pull request
